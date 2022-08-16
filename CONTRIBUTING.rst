#####################
Contributing Guide
#####################

Thank you so much for considering contributing to the project! Below you'll find the basic steps required to contribute to the project,
from setup to pull request.

Add a feature, fix a bug, or write documentation
-------------------------------------------------

#. `Fork this repository`_ on GitHub: Make your own copy of the repository. Once you've made changes to your own version, you will create a pull request to merge your changes into the main repository.

#. Clone the forked repository: Clone your forked version of the repository to your local machine so that you can make edits to it.

   
   .. code:: console

        git clone git@github.com:YOUR_GITHUB_USERNAME/chat-analyzer.git

#. Create a new branch: Create a new branch for each different type of feature/fix/edit you would like to make in your forked repository. 
   Each pull request you eventually make should correspond to a single feature, fix, or edit. This allows for an easier review process & improves 
   the overall quality of the commit history.

   .. code:: console

       cd chat-analyzer
       git checkout -b <branch_name>

   The ``<branch_name>`` should be a short, descriptive name for the feature being worked on. i.e: "add-foo-field", "fix-issue-24", "refactor-help-cmd", etc...

#. Set up your enviornment by installing the developer dependencies: Certain dependencies are used for development that are not required 
   for standard usage. These dependencies allow you to do things such as run tests, build documentation, lint your code, etc...

   .. code:: console

       pip install -e ".[dev]"

#. **Make your changes**: You are now ready to make all of the changes/additions you want to contribute to the project!

#. *[SKIP FOR NOW]:* Testing w/ ``pytest`` is not yet implemented, so you can ignore this step for now. It will eventually happen at this step.

#. *[SKIP FOR NOW]:* Linting w/ ``flake8`` is not yet implemented, so you can ignore this step for now. It will eventually happen at this step.
    
    .. See https://raw.githubusercontent.com/xenova/chat-downloader/master/docs/contributing.rst to see his testing section example
    .. TODO: add: "After tests pass:"

#. As you make your changes, `add`_ the new/modified files and
   `commit`_ the files, adding a commit a message with ``-m "<message>"`` that abides by the `Conventional Commits specification`_. 
   *Do not commit files until they have been tested and linted (see previous two steps).*
   After fully completing the change you wish to add to the main codebase,
   `push`_ the commits.

   .. code:: console

       git add path/to/code.py
       git commit -m 'message'
       git push origin <branch_name>

   If the change you are making is large or has slightly different components, consider chunking the changes into separate commits. For example:

   .. code:: console

       git add chat_analyzer/cli.py
       git add chat_analyzer/analyzer.py
       git commit -m 'feat: added foo command'
       git add docs/
       git commit -m 'docs: guide covers foo command'
       git push origin add-foo-command

#. `Create a pull request`_: Once pushing your final changes to the branch in your forked repository,
   create a pull request from your forked repository on GitHub to the main branch of the Chat Analyzer repository.

**All done!** - Your changes will be reviewed and merged into the main repository by the maintainers. Thanks again for contributing to the project :)

.. _Fork this repository: https://github.com/David-Fryd/chat-analyzer/fork
.. _add: https://git-scm.com/docs/git-add
.. _commit: https://git-scm.com/docs/git-commit
.. _Conventional Commits specification: https://www.conventionalcommits.org/en/v1.0.0/#summary 
.. _push: https://git-scm.com/docs/git-push 
.. _Create a pull request: https://help.github.com/articles/creating-a-pull-request
