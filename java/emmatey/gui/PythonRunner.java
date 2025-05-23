package emmatey.gui;

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

    private static String getExecutablePath(String jarPath) {
        String os = System.getProperty("os.name").toLowerCase();
        String exeName;

        if (os.contains("win")) {
            exeName = "output.exe";
        } else {
            exeName = "output";
        }

        String exePath = jarPath + File.separator + exeName;
        System.out.println("this is the exePath: " + exePath);
        return exePath;
    }

    public static List<String> runPreview(String inputFilePath) {
        List<String> departments = new ArrayList<>();

        try {
            String jarPath = MediaHandler.locateJar();
            String exePath = getExecutablePath(jarPath);

            ProcessBuilder pb = new ProcessBuilder(
                exePath,
                inputFilePath,
                ".",
                "--preview"
            );
            pb.directory(new File(jarPath));
            pb.redirectErrorStream(true);

            Process process = pb.start();

            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream())
            );

            String currentLine;
            while ((currentLine = reader.readLine()) != null) {
                departments.add(currentLine);
            }

            process.waitFor();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }

        return departments;
    }

    public static void runGenerate(String inputFilePath, String outputPath, List<String> selectedDepartments) {
        List<String> command = new ArrayList<>();

        try {
            String jarPath = MediaHandler.locateJar();
            String exePath = getExecutablePath(jarPath);

            command.add(exePath);
            command.add(inputFilePath);
            command.add(outputPath);
            command.add("--departments");
            for (String dept : selectedDepartments) {
                command.add(dept);
            }

            System.out.println("This is the command sent to python: " + command);
            ProcessBuilder pb = new ProcessBuilder(command);
            pb.redirectErrorStream(true);
            pb.directory(new File(jarPath));

            Process process = pb.start();

            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream())
            );

            String currentLine;
            while ((currentLine = reader.readLine()) != null) {
                System.out.println(currentLine);
            }

            process.waitFor();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}