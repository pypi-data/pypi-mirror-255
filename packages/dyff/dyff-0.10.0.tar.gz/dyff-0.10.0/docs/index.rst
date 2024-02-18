.. meta::
    :description: Dyff is a cloud platform for running scalable and reproducible \
        evaluations of AI/ML systems without revealing information about test \
        datasets or systems under test.

Dyff documentation
==================

Dyff is a cloud platform for running scalable and reproducible evaluations of
AI/ML systems without revealing information about test datasets or systems under
test.

Why is Dyff important?
----------------------

- **Scalable and reproducible**: Thorough evaluations need to be a routine part of
  system deployment ala CI/CD, so the process needs to be low-friction and
  consistent across models.

- **Data privacy**: In our ideal world, performance scores are economically valuable
  because they're tied to public perceptions of trustworthiness, insurance
  premiums, etc. There will be an incentive to increase scores (which is good!),
  but it is trivial to score well on any given evaluation by training on the
  test data, so it has to be private.

- **System privacy**: The only way to ensure data privacy is for data never to leave
  our system. Thus, system creators have to submit their systems to us. These
  systems can be extremely valuable business assets, so nobody will do that
  unless we can protect their property.

Get started
-----------

To take your first steps with Dyff, visit :doc:`tutorials/creating-a-dataset`.

.. toctree::
   :hidden:

   user-guide/index.rst
   tutorials/index.rst
   examples/index.rst
   api-reference/index.rst
   development/index.rst
   deployment/index.rst
   releases/index.rst

Indices and tables
------------------

-  :doc:`releases/index`
-  :ref:`genindex`
-  :ref:`modindex`
-  :ref:`search`
