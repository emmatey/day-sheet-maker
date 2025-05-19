import java.util.List;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

public class ElementTester {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("UI element test enviroment");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(800, 800);

            JButton testButton = saveDirPicker.createButton(path -> {
                System.out.println("User chose: " + path);
                JOptionPane.showMessageDialog(null, "You chose: " + path);
            });
            
            JButton filePickerButton = FilePickerButton.createButtonWithCallback(path -> {
            String selectedFilePath = path;
            List<String> validDepartments = PythonRunner.runPreview(selectedFilePath);
            List<String> selectedDepartments = DepartmentSelectionDialog.showSelectDialog(validDepartments);
            System.out.println(selectedDepartments);
            });

            JPanel panel = new JPanel();
            panel.add(testButton);
            panel.add(filePickerButton);

            frame.getContentPane().add(panel);
            frame.setVisible(true);
        });
    }
}
