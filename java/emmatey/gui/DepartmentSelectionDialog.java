package emmatey.gui;

//this dialogue requires a list of strings from the getValidDepts() python funciton.
import java.awt.Dimension;
import java.awt.GridLayout;
import java.io.File;

import javax.swing.*;

import java.util.ArrayList;
import java.util.List;

public class DepartmentSelectionDialog{
    
    public static List<String> showSelectDialog(List<String> departments){
       // List of pointers to checkbox instances
       List<JCheckBox> checkboxes = new ArrayList<>();

       // Holder pannel to be passed to JOptionPane
       JPanel holderPanel = new JPanel();
       holderPanel.setLayout(new BoxLayout(holderPanel, BoxLayout.Y_AXIS));

       // Checkbox Panel
       JPanel checkboxPanel = new JPanel();
       checkboxPanel.setLayout(new GridLayout(4, 3));
       holderPanel.add(checkboxPanel);
       
       // Button Panel
       JPanel buttonPanel = new JPanel();
       buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.X_AXIS));
       holderPanel.add(buttonPanel);

       // Select All Button
        JButton selectAll = new JButton("Select All");
        selectAll.addActionListener(event -> {
            for (JCheckBox cb : checkboxes) {
                cb.setSelected(true);
            }
        });
        buttonPanel.add(selectAll);
        buttonPanel.add(Box.createRigidArea(new Dimension(7, 0)));  // horizontal gap between buttons

        // De-Select All Button
        JButton deselectAll = new JButton("De-Select All");
        deselectAll.addActionListener(event -> {
            for (JCheckBox cb : checkboxes) {
                cb.setSelected(false);
            }
        });
        buttonPanel.add(deselectAll);

       // Dept Checkboxes
       for(String dept : departments){
        JCheckBox box = new JCheckBox(dept);
        checkboxes.add(box);
        checkboxPanel.add(box);
        }

       // Add Scrollbar Functionality
        JScrollPane scrollPaneWrapper = new JScrollPane(holderPanel);

       // Add Picture
       ImageIcon gifIcon = MediaHandler.getGifIcon("danceSkeleton.gif");
       
       // Move JOptionPane Buttons
       UIManager.put("OptionPane.buttonOrientation", SwingConstants.LEFT);

       // Call JOptionPane Helper
        int returnValue = JOptionPane.showConfirmDialog(
        null,
        scrollPaneWrapper,
        "Select Departments",
        JOptionPane.OK_CANCEL_OPTION,
        JOptionPane.PLAIN_MESSAGE,
        gifIcon
        );

       // Add selected depts to list for later processing.
        List<String> selectedDepartments = new ArrayList<>();
        if (returnValue == JOptionPane.OK_OPTION){
            for (JCheckBox cb : checkboxes){
                if (cb.isSelected()== true){
                    selectedDepartments.add(cb.getText());
                }
            }
        }
        return selectedDepartments;
    }  
}