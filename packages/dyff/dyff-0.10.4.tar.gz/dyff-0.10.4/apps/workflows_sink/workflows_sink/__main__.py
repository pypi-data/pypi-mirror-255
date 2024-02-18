# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import absl.app
from absl import logging

from .main import WorkflowsSink


def main(unused_argv):
    logging.set_verbosity(logging.DEBUG)

    app = WorkflowsSink()
    app.run()


if __name__ == "__main__":
    absl.app.run(main)
