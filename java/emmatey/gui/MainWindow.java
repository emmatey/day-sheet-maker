import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;

public class MainWindow implements Runnable {
    private String selectedFilePath;

    public void run() {
     JFrame frame = new JFrame("Emma wuz here");  
     frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
     frame.setSize(600, 480);
     frame.setLocationRelativeTo(null); //null argument sets frame to center of screen

     //Header Panel
     JPanel header = new JPanel();
     header.setBackground(new Color(253, 187, 244)); 
     header.setPreferredSize(new Dimension(800, 75));
     
     JLabel header_text = new JLabel("💗 Daily Staffing Sheet Generator 💗", SwingConstants.CENTER);
     header_text.setFont(new Font("SansSerif", Font.BOLD, 24));
     header_text.setHorizontalAlignment(SwingConstants.CENTER);
     header.add(header_text);
     
     //Create Content Panel, vertical stack button layout
     JPanel contentPanel = new JPanel();
     contentPanel.setBackground(new Color(119, 221, 119));
     contentPanel.setLayout(new BoxLayout(contentPanel, BoxLayout.Y_AXIS));

     //Add File Picker Button
     JButton filePickerButton = FilePickerButton.createButtonWithCallback(path -> {
        selectedFilePath = path;
        System.out.println(path);
     });
     filePickerButton.setAlignmentX(Component.CENTER_ALIGNMENT);
     filePickerButton.setFont(new Font("Monospaced", Font.BOLD, 16));
     filePickerButton.setPreferredSize(new Dimension(250, 50));
     filePickerButton.setMaximumSize(new Dimension(250, 50));
     contentPanel.add(filePickerButton);

     //Add panels to frame
     frame.getContentPane().add(header, BorderLayout.NORTH);
     frame.getContentPane().add(contentPanel, BorderLayout.CENTER);
     frame.setVisible(true);
    }
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new MainWindow());
    }
}

