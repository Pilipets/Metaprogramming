<h2>Java code formatting or prettifying console application</h2>


<h4>Description:</h4>
Briefly, the app uses command-line arguments to either format or verify .java files collected from the given directory, project, file location. The user can adjust formatting, verification options through a custom or default configuration file.


<h4>Usage instructions:</h4>
<ol>
    <li>Use <b>--admin</b> command-line option to run <i>run_debug(...)</i> method from <i>java_formatter_ui.py</i> - debug purposes. You can modify this method as you want.</li>
    <li>Use <b>--help</b> cmd argument to print the description info.</li>
    <li>The app supports up to 4 additional arguments:
        <ul>
        <li><b>input_path{'string'}</b> - required argument. It is a relative or absolute path to the folder, project, file, that is expecting to be processed by the app;</li>
        <li><b>option{-(p|d|f)}</b> - required argument. Specifies the execution policy - directory recursively, directory without recursion, one file. The app uses the input path and provided option argument to get the files with .java format that don't start with <i>'formatted_'</i>, <i>'verified_'</i> prefixes - those prefixes are reserved;</li>
        <li><b>(--config|-c)=path</b> - optional argument. If not provided, options from <i>config/config_handler.py</i> are used. Specifies the code formatting options - the user can view all the supported options in the <i>config/default_config.json</i> file;</li>
        <li><b>action{--beautify, -b, --verify, -v}</b> - optional argument. Specifies the execution mode: either formats or verifies the input files considering config and <b>'option'</b> argument, locates the result files in the input_path directory with the prefixes <i>'formatted_'</i> and <i>'verified_'</i> respectively.</li>
        </ul>
   </li>
   <li>To <b>RUN</b> the application, you must execute <i>java_formatter_app.py</i> script with the respective arguments, ending with the <i>input_path</i>.</li>
</ol>