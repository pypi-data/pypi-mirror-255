# Design Document for Audit Developer API

## Vocabulary (italic == not implemented)

- Output -- raw output of the system under test (SUT)
- Report -- Distillation of output into meaningful instance-level data
  - Represented as `pandas.DataFrame`s (actually PyArrow files in Parquet format that are converted to DFs when loaded; PyArrow files have a schema with static datatypes)
  - Reports run in batch mode on k8s because they can take a long time for large datasets / outputs
  - Example: `classification.ClassificationErrors` report contains the columns `["_index_", "top1", "top5"]`, where `top1` and `top5` are `1` if the predicted label was correct and `0` otherwise
- _Audit_ -- An algorithm composed of a hierarchy of `Test`s to run against a single SUT in order to produce an `AuditDocument`.
- _AuditDocument_ -- The "rendered" result of running an `Audit`
- _Test_ -- An algorithm mapping one or more `Report` DFs for the same SUT to one or more test result events. (c.f. Python's `unittest` library)
  - Some events are _assertions_, which either _pass_ or _fail_
    - e.g., `unittest.TestCase.assertTrue(<not biased>)`
  - Some events _display_ results in the audit document. (Similar to Jupyter's `display()` or `matplotlib` functionality.)
  - Some events generate _scores_ that are saved in a known location and can be used for comparing results of multiple audits.
    - Scores could be structured DFs -- they have a schema and defined semantics for each column (e.g., is lower or higher better?)
    - They could also just be JSON objects -- if the scores are mostly scalars it feels weird to put them in DataFrames.
    - Used to build leaderboards, "which model is the least biased?"
- _LeaderBoard_ -- A Web widget that allows quick comparison of all the systems that have been audited using the same `Audit`
  - The leaderboard backend picks up the scores from each audit and runs user queries against them.
  - The UI allows basic analysis like filtering and sorting
  - Possibly also exposes an interpreter that can run Pandas operations on the scores DF.

## Auditor API

I'm imagining this as a sort of document template system that allows static content and computed values to be interleaved.

The slickest way to do this might be something like Markdown with special syntax for embedding Python code (c.f. "literate programming"). Introducing DSLs can be risky because developers might decide that the DSL is too complicated to be worth learning. For our application, though, I think we could do something very simple like pulling out all the code, concatenating and running it as a single script, then inserting outputs in the appropriate places.

Mockup of the "literate programming" approach, using Jinja-like template syntax and imagining that the "text" part is Markdown:

```
# Facepaint Audit

This audit tests the robustness of face recognition systems to subjects wearing face paint

## Accuracy

{%
report_id = api.query_reports(
    datasetName="Faces-HeimlichCountyFair",
    report="classification.ClassificationErrors"
)[0]
df = api.get_report_data(report_id)
accuracy = df.groupby("facepaint").mean()
no_paint = accuracy[accuracy["facepaint"] == 0]
yes_paint = accuracy[accuracy["facepaint"] == 1]
differential = (no_paint["top1"] - yes_paint["top1"]).item()

score("DifferentialAccuracyForFacepaint", differential)
plot(data=accuracy, x="facepaint", y="top1")
test_passes = assertTrue(
    differential < 0.1,
    pass_text="The solution's performance was not degraded by facepaint.",
    fail_text="The solution performs *worse* for subjects wearing facepaint."
)
%}

Your solution {{"is bad and you should feel bad!" if not test_passes else "is fine, I guess."}}
```

This translates pretty directly to Python code:

```python
from alignmentlabs.dyff import api
audit = api.Audit()

audit.text(
f"""# Facepaint Audit

This audit tests the robustness of face recognition systems to subjects wearing face paint

## Accuracy
"""
)

report_id = api.query_reports(
    datasetName="Faces-HeimlichCountyFair",
    report="classification.ClassificationErrors"
)[0]
df = api.get_report_data(report_id)
accuracy = df.groupby("facepaint").mean()
no_paint = accuracy[accuracy["facepaint"] == 0]
yes_paint = accuracy[accuracy["facepaint"] == 1]
differential = (no_paint["top1"] - yes_paint["top1"]).item()

audit.score("DifferentialAccuracyForFacepaint", differential)
audit.plot(data=accuracy, x="facepaint", y="top1")
test_passes = audit.assertTrue(
    differential < 0.1,
    pass_text="The solution's performance was not degraded by facepaint.",
    fail_text="The solution performs *worse* for subjects wearing facepaint."
)

audit.text(
f"""
Your solution {"is bad and you should feel bad!" if not test_passes else "is fine, I guess."}
"""
)

audit.render()
```

Basically it's a choice between whether the text or the code needs to be escaped.

An alternative is to have a more structured Python representation:

```python
class DifferentialAccuracyForFacepaint(Test):
    def description(self) -> str:
        """Optional text explaining the test."""
        return None

    def requires(self) -> List[Type[Report]]:
        """List of Reports needed to do the test."""
        return [api.reports.classification.ClassificationErrors]

    def run(self):
        """Do computations and test assertions here."""
        df = self.get_report_data(api.reports.classification.ClassificationErrors)
        self.accuracy = df.groupby("facepaint").mean()
        self.no_paint = accuracy[accuracy["facepaint"] == 0]
        self.yes_paint = accuracy[accuracy["facepaint"] == 1]
        self.differential = (self.no_paint["top1"] - self.yes_paint["top1"]).item()

        self.assertTrue(
            self.differential < 0.1,
            "The system's accuracy is lower for subjects wearing face paint."
        )

    def scores(self):
        """Return the performance scores from this test that can be used to compare solutions."""
        return {"DifferentialAccuracyForFacepaint": self.differential}

    def table(self) -> pandas.DataFrame:
        """Render the result of the test as a Table."""
        return accuracy

    def plot(self, plotter):
        """Render the result of the test as a plot."""
        plotter.barplot(data=self.accuracy, x="facepaint", y="top1")

    def conclusion(self) -> str:
        """Describe the test results in text."""
        if self.differential < 0.1:
            return "The solution's performance was not seriously degraded by facepaint."
        else:
            return "The solution performs *worse* for subjects wearing facepaint."


audit = Audit(
    Text("This audit tests a face recognition system's ability to recognize people wearing face paint."),
    Section("Accuracy",
        DifferentialAccuracyForFacepaint()
    )
)
```

Naturally, we will provide commonly-used `Test`s in our API. For example, we would probably have a parameterized `DifferentialAccuracy(field: str, threshold: float)` implementation.

Our system would run the `Audit` instance to generate an `AuditDocument` and also pull out any scores output by any of the `Test`s and save them so that they can be used in LeaderBoards. Entries in the LeaderBoards would then link back to the generated `AuditDocument`.

There could be multiple rendering engines, in particular one that generates Web pages and one that generates PDFs.
