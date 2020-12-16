<h2>Java code convention modifying console application</h2>

<h4>Description:</h4>
Briefly, the app uses command-line arguments to format names and generate JavaDoc in
.java files collected from the given directory, project, file according to the convention.<br>Creates RENAMED.log with all the convention fixes and may generate 'modified_*.java files depending on the given command-line arguments.

<h4>Usage instructions:</h4>
<ol>
    <li>Use <b>--admin</b> command-line option to run <i>run_debug(...)</i> method from <i>java_modifier_ui.py</i> - debug purposes. You can modify this method as you want.</li>
    <li>Use <b>--help</b> cmd argument to print the description info.</li>
    <li>The app supports up to 4 additional arguments:
        <ul>
        <li><b>input_path{'string'}</b> - required argument. It is a relative or absolute path to the folder, project, file; that is expecting to be processed by the app. Must be the last execution argument;</li>
        <li><b>option{-(p|d|f)}</b> - required argument. Specifies the execution policy - directory recursively, directory without recursion, one file. The app uses the input path and provided option arguments to get the files with .java format that don't start with <i>'modified_'</i> aka reserved prefix;</li>
        <li><b>option{--doc}</b> - optional argument. Specifies that the app will validate/generate JavaDoc for top-level classes, methods. If not provided, only the renaming part is done;</li>
        <li><b>action{--modify, -m, --verify, -v}</b> - optional argument. Specifies the execution mode: either modifies or verifies the input files considering <b>'option'</b> arguments. If (-m|--modify) flag is set, creates <i>'modified_*.java'</i> files with the applied convention fixes.</li>
        </ul>
   </li>
   <li>To <b>RUN</b> the application, you must execute the <i>__main__.py</i> script with the respective arguments, ending with the <i>input_path</i>.<br>Example: "python3 CodeConventionModifier\(Java\)/src/__main__.py -m -d --doc /mnt/e/Documents/input_files".</li>
</ol>