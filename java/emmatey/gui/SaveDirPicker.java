import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.io.File;
import java.util.function.Consumer;

import javax.swing.JButton;
import javax.swing.JFileChooser;

public class SaveDirPicker {

    public static JButton createButton(Consumer<String> saveLoc){
        JButton saveButton = new JButton("Choose Save Location");
        saveButton.setAlignmentX(Component.CENTER_ALIGNMENT);
        saveButton.setFont(new Font("Monospaced", Font.BOLD, 16));
        saveButton.setPreferredSize(new Dimension(250, 50));
        saveButton.setMaximumSize(new Dimension(250, 50));
        saveButton.setEnabled(false);

        saveButton.addActionListener(event -> {
            // Spawn
            JFileChooser fileChooser = new JFileChooser();

            // Modify
            fileChooser.setApproveButtonText("Confirm Save Location");
            fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);

            // play music
            File songPath = new File("../assets/thinkMusic.wav");
            MediaHandler.playSound(songPath, false);

            // return
            int returnVal = fileChooser.showDialog(null, "Choose Save Location");

            // Add User Selection to Consumer
            if(returnVal == JFileChooser.APPROVE_OPTION){
                File selectedSaveLoc = fileChooser.getSelectedFile();
                String saveFilePath = selectedSaveLoc.getAbsolutePath();
                saveLoc.accept(saveFilePath);
                }
            });
            return saveButton;
        };
    }
