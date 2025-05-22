package emmatey.gui;

import javax.sound.sampled.*;
import javax.swing.*;
import java.io.File;
import java.io.IOException;

public class MediaHandler {
    private static Clip activeClip;

    public static void playSound(File audioFilePath, boolean loop){
        // Stop any currently playing sounds
        stopSound();

        // Create Audio Input Stream
        try {
        System.out.println("Trying to load wav from: " + audioFilePath.getAbsolutePath());
        System.out.println("Exists? " + audioFilePath.exists());
        AudioInputStream audioStream = AudioSystem.getAudioInputStream(audioFilePath);

        // Create Clip Object
        Clip audioClip = AudioSystem.getClip();
        audioClip.open(audioStream);
        activeClip = audioClip;

        // Play Audio, and Loop if Specified
        if (loop == true){
            activeClip.loop(Clip.LOOP_CONTINUOUSLY);
        } else {
            activeClip.start();
        }

        } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e) {
            e.printStackTrace();
        }
    }

    public static void stopSound() {
        if (activeClip != null) {
            if (activeClip.isRunning()){
                activeClip.stop();
            }
            activeClip.close();
            activeClip = null;
        }
    }

    public static JLabel getGifLabel(File gifPath){
        // Create JLabel
        JLabel gifLabel = new JLabel();
        File gifFile = gifPath;
        System.out.println("Trying to load gif from: " + gifFile.getAbsolutePath());
        System.out.println("Exists? " + gifFile.exists());
       
        // Create Icon
        ImageIcon gifIcon = new ImageIcon(gifFile.getAbsolutePath());

        // Add Icon to Label
        gifLabel.setIcon(gifIcon);

        // Return
        return gifLabel;
        }
}
