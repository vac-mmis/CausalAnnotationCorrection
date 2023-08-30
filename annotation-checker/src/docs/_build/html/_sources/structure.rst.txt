
GUI
====

Navbar
^^^^^^


.. image:: _static/res/navbar.png
   :target: _static/res/navbar.png
   :alt: navbar.png


Click on ``Check`` to check the annotation. ``Save`` will save all changes that were made. ``Show All`` displays all errors found for the given annotation and model inside the output window.
Click on ``Dictionary`` to open the dictionary.

Dictionary
^^^^^^^^^^


.. image:: _static/res/dict.png
   :target: _static/res/dict.png
   :alt: dict.png

With the ``Dictionary`` you can tell the spell check to include or exclude words. Inside the dictionary, enter a word and click add to add it to the dictionary. Click on words that has been added to select them and click 'Remove' to delete them from the dictionary.

Annotation Editor
^^^^^^^^^^^^^^^^^


.. image:: _static/res/anno_editor.png
   :target: _static/res/anno_editor.png
   :alt: anno_editor.png


Here you can see all open annotations. You can click on the tabs to switch between multiple loaded annotations.
The errors that were found during the check are highlighted. Click on them for further information. 
You will also get advices for fixing the errors if possible. 
You can select the line limit to have only a certain number 
of lines checked by clicking on the desired number of lines 

Model Editor
^^^^^^^^^^^^


.. image:: _static/res/model_editor.png
   :target: _static/res/model_editor.png
   :alt: model_editor.png


Inside the model window you can view and edit the domain and problem file. 

Check Options
^^^^^^^^^^^^^


.. image:: _static/res/checks.png
   :target: _static/res/checks.png
   :alt: checks.png


The ``Checks`` panel contains information for each check applied to the annotation. The checks are divided into two groups:

* ``Continuous Checks`` are running everytime you press check.
* ``Sequential Checks`` are executed one after another and if a check throws an error, the checking process will stop. It will move on if all error thrown by the actual checker are fixed.

You can toggle them off to deactivate them during the checking process. 
The gear button opens the menu for configuring the check.
The second button shows the log that is potentially generated during the execution. 
Click on the colored badge that shows the number of errors found by this check to automatically scroll to the first error found. 
Green means no errors. Yellow means there are only warnings, but they do not disturb the general process. 
Red means errors have been found that need to be taken care of.

Output
^^^^^^


.. image:: _static/res/output.png
   :target: _static/res/output.png
   :alt: _static/output.png


The Output window displays all errors found in the clicked section of the annotation. If you click on one, you will get a selection of correction suggestions and information about the error. These are:


* ReplaceSequence:
    Replaces the section with a suggestion
* RemoveSequence:
    Removes the sequence
* WhitelistSignature:
    Saves the signature of an action as the active signature. Same actions, with more or less parameters, are now marked as errors.
* Alert:
    Outputs more information about the error.
* AdaptModel:
    If you want to adapt the model, for example by adding actions or objects, AdaptModel copies a template to the clipboard, which you can directly take over and adapt afterwards.
