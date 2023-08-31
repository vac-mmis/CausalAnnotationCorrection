Usage
======

After the package has been installed, just use:

.. code-block::

   $ acheck check $domain.pddl $problem.pddl $annotation.csv

By default, it will automatically start a local server on `127.0.0.1:9000 <http://127.0.0.1:9000/>`_.

Options
--------


* 
  ``-l $file_1 $file_2 $file_n`` : Enter one or multiple annotation files or the domain or problem file to lock them in editor

  .. code-block::

       $ acheck check domain.pddl problem.pddl anno_1.csv -l domain.pddl anno_1.csv

* 
  ``-o $directory``\ : Enter a custom directory for all output files. 

  .. code-block::

       $ acheck check domain.pddl problem.pddl anno_1.csv -o project/output

* ``-p port``\ : Specify the ``port`` on which the server is running. 
  .. code-block::

       $ acheck check domain.pddl problem.pddl anno_1.csv -p 8000

* 
  ``-v``\ : Enable verbose output. 

* 
  ``-m directory``\ : Enter a custom ``directory`` to load multiple annotations

* 
  ``--nogui``\ : For command line only use. 

* 
  ``--inplace``\ : Work with the original files. For command line only use without backup. 

.. warning::

    Working with ``--inplace`` means that you are working with the original files. Be aware that there is no backup.


Customizing the config
-----------------------

1. First export the config file, so that you can modify it locally:

.. code-block::

        $ acheck config -e local_config.toml

2. Import back yur local changes:

.. code-block::

        $ acheck config -i local_config.toml

3. To reset the config to default settings, just import an empty file and start the application.