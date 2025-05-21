import java.util.List;

import javax.swing.*;

public class ConfirmAndExitProgramDialogue extends JDialog {

    public static void handleSave(String selectedFilePath, String savePath, List<String>selectedDepartments){
        System.out.println(savePath);
        PythonRunner.runGenerate(
        selectedFilePath, 
        savePath, 
        selectedDepartments);
     };
    
    public static void showDialog(String selectedFilePath, String savePath, List<String>selectedDepartments){
        //Final Dialogue. This window will have a picture
        //pannel, a loading bar, and a final close button
        //that will end the program and open saveloc
        //Will need one save and exit button
        //one loading bar
        //one photo framer 

        //Create Parrent Window
        JDialog dialogue = new JDialog();

        //Create Holder Panel
        JPanel holder = new JPanel();
        holder.setLayout(new BoxLayout(holder, BoxLayout.Y_AXIS));

        //Create Photo Panel
        JPanel photoFrame = new JPanel();
        //placeholder
        JLabel pic = new JLabel(new ImageIcon("skeleton-dance.gif"));
        pic.setAlignmentX(CENTER_ALIGNMENT);
        photoFrame.add(pic);
        //placeholder
        holder.add(photoFrame);

        //Create Progress Bar
        JProgressBar progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setString("Generating Day Sheets....Beep Boop");
        progressBar.setStringPainted(true);
        holder.add(progressBar);

        //Create JButton, Confirm and Close
        JButton closeButton = new JButton("Zip It Up \n & \n Zip..It..Out!");
        closeButton.addActionListener(event -> {
        });
        holder.add(closeButton);

        //Create Background Thread
        SwingWorker lilLoader = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground(){
                handleSave(selectedFilePath, savePath, selectedDepartments);
                return null;
            }
            
            @Override
            protected void done(){
                progressBar.setIndeterminate(false);

            }
        };
        //Add panels to frame
        dialogue.add(holder);
        dialogue.pack();
        dialogue.setVisible(true);

        lilLoader.execute();

    }

}
