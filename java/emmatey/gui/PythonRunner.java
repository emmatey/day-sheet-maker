import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.ProcessBuilder;
import java.util.ArrayList;
import java.util.List;
 
//**From Output.py for context**
//if __name__ == "__main__":
//    """
//    Command-line entry point.
//
//    Usage:
//        python output.py <input_file> <save_directory>
//        --departments
//            a list of the departments to be processed and output. chosen by user from GUI
//        --preview
//            prints [FindValidDepts()]
//    """

public class PythonRunner {

    public static List<String> runPreview(String inputFilePath) {
        List<String> departments = new ArrayList<>();

        try {
            ProcessBuilder pb = new ProcessBuilder(
                "python3",
                "output.py",
                inputFilePath,
                ".",
                "--preview"
            );
            pb.directory(new File("../python/src"));

            Process process = pb.start();

            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream())
            );

            String currentLine = reader.readLine();
            while (currentLine != null) {
                departments.add(currentLine);
                currentLine = reader.readLine();
                ;}

            process.waitFor();
 
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }

        return departments;
    }

    public static void runGenerate(String inputFilePath, String outputPath, List<String> selectedDepartments) {
        List<String> command = new ArrayList<>();

        command.add("python3");
        command.add("output.py");
        command.add(inputFilePath);
        command.add(outputPath);
        command.add("--departments");

        for (String dept : selectedDepartments) {
            command.add(dept);
        }

        try {
            ProcessBuilder pb = new ProcessBuilder(command);
            pb.directory(new File("../python/src"));

            Process process = pb.start();

            process.waitFor();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}