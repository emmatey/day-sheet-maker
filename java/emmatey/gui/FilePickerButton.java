import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.io.File;
import java.util.function.Consumer;

import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.filechooser.FileNameExtensionFilter;

public class FilePickerButton{

    public static JButton createButtonWithCallback(Consumer<String> onFilePicked){
       JButton button = new JButton("Choose Input File");
       button.setToolTipText(".exe or .xlsx; whole store schedule.");
       button.setAlignmentX(Component.CENTER_ALIGNMENT);
       button.setFont(new Font("Monospaced", Font.BOLD, 16));
       button.setPreferredSize(new Dimension(250, 50));
       button.setMaximumSize(new Dimension(250, 50));
      
       button.addActionListener(event -> {
        JFileChooser fileChooser = new JFileChooser();
        FileNameExtensionFilter filter = new FileNameExtensionFilter(
            "Spreadsheet Files (.xlsx, .csv)", "xlsx", "csv"
        );
        fileChooser.setFileFilter(filter);
        
        //opens file chooser, and returns a value of 0 if file is picked, 1 if not, -1 if err
        int result = fileChooser.showDialog(null, "Select Input File"); 

        //APPROVE_OPTION is a 'constant' equal to int 0 if a file is chosen.
        if (result == JFileChooser.APPROVE_OPTION){
            File selectedFile = fileChooser.getSelectedFile();
            String absolutePath = selectedFile.getAbsolutePath();
            //add to consumer
            onFilePicked.accept(absolutePath);
            }
        });
       return button;
    }
}
