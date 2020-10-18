<h2>Java code formatting or prettifying console application</h2>


<h4>Description:</h4>
Briefly, the app uses command-line arguments to either format or verify .java files collected from the given directory, project, file location. The user can adjust formatting, verification options through a custom or default configuration file.


<h4>Usage instructions:</h4>
<ol>
<li>Use <b>--admin</b> command-line option to run <i>run_debug(...)</i> method from <i>java_formatter_ui.py</i> - debug purposes.
You can modify this method as you want.</li>
<li>Use <b>--help</b> cmd argument to print the description info.</li>
<li>The app supports up to 4 additional arguments:
<ul>
<li><b>input_path{'string'}</b> - required argument. It is a relative or absolute path to the folder, project, file,
that is expecting to be processed by the app;</li>
<li><b>option{-(p|d|f)}</b> - required argument. Specifies the execution policy - directory recursively, directory without recursion, one file.
The app uses the input path and provided option argument to get the files with .java format that don't start with <i>'formatted_'</i>, <i>'verified_'</i> prefixes - those prefixes are reserved;</li>
<li><b>(--config|-c)=path</b> - optional argument.
If not provided, options from <i>config/config_handler.py</i> are used. Specifies the code formatting options - the user can view all the supported options in the <i>config/default_config.json</i> file;</li>
<li><b>action{--beautify, -b, --verify, -v}</b> - optional argument.
Specifies the execution mode: either formats or verifies the input files considering config and <b>'option'</b> argument,
locates the result files in the input_path directory with the prefixes <i>'formatted_'</i> and <i>'verified_'</i> respectively.</li>
</ul> </li> </ol>

<h4>Further optimizations:</h4>
<ul>
<li>Produce a stream of tokens from the <i>JavaFormatterCore.format(...)</i> method rather than the string - this will allow easier control for the amount of the blank lines as well as increase the performance of the <i>JavaFormatterCore.verify(...)</i> method by avoiding tokenizing the output;</li>
<li>Provide errors handling the way it's done in the <i>java_lexer.py</i> with silent mode and error list;</li>
<li>Combine similar blocks of code to avoid a lot of if-clauses in the format_separator method;</li>
<li>Add javadoc formatting options to the configuration file, format javadoc;</li>
<li>Don't delete all the whitespace characters and set them again - adjust the amount if needed;</li>
<li>If the input data is damaged, the formatting will be broken from some point - change that logic to handle that by clearing the stack of potentially wrong items when encountered one. This mode will be a kind of recovery - others can be silent, panic.</li></ul>