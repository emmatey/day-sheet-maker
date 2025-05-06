import javax.swing.*;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;

public class MainWindow implements Runnable {
    public void run() {
     JFrame frame = new JFrame("Emma wuz here");  
     frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
     frame.setSize(600, 480);
     frame.setLocationRelativeTo(null); //null argument sets frame to center of screen
     frame.setVisible(true);

     //Header Panel
     JPanel header = new JPanel();
     header.setBackground(new Color(253, 187, 244)); 
     header.setPreferredSize(new Dimension(800, 75));
     
     JLabel header_text = new JLabel("💗 Daily Staffing Sheet Generator 💗", SwingConstants.CENTER);
     header_text.setFont(new Font("SansSerif", Font.BOLD, 24));
     header_text.setHorizontalAlignment(SwingConstants.CENTER);
     header.add(header_text, BorderLayout.CENTER);
     
     //Create Content Panel, vertical stack button layout
     JPanel contentPanel = new JPanel();
     contentPanel.setBackground(new Color(119, 221, 119));
     contentPanel.setLayout(new BoxLayout(contentPanel, BoxLayout.Y_AXIS));

     //Add to frame
     frame.getContentPane().add(header, BorderLayout.NORTH);
     frame.getContentPane().add(contentPanel, BorderLayout.CENTER);

    }
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new MainWindow());
    }
}

