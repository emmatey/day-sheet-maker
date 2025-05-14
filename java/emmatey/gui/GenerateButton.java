import javax.swing.JButton;

public class GenerateButton {

    public static JButton createGeneraButton(String filePath){
        JButton button = new JButton("Generate");
       
        button.addActionListener(input -> {
        try {
            ProcessBuilder pb = new ProcessBuilder("python3", "output.py", filePath);
            
        }
        });
        return button;
    }
}