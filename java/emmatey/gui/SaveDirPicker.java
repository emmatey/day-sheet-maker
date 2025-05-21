import java.io.File;
import java.util.function.Consumer;

import javax.swing.JButton;
import javax.swing.JFileChooser;

public class SaveDirPicker {

    public static JButton createButton(Consumer<String> saveLoc){
        JButton saveButton = new JButton("Choose Save Location");

        saveButton.addActionListener(event -> {
            //Spawn
            JFileChooser fileChooser = new JFileChooser();

            //Modify
            fileChooser.setApproveButtonText("Confirm Save Location");
            fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);

            //Display
            int returnVal = fileChooser.showDialog(null, "Choose Save Location");

            //Add User Selection to Consumer
            if(returnVal == JFileChooser.APPROVE_OPTION){
                File selectedSaveLoc = fileChooser.getSelectedFile();
                String saveFilePath = selectedSaveLoc.getAbsolutePath();
                saveLoc.accept(saveFilePath);
                }
            });
            return saveButton;
        };
    }
