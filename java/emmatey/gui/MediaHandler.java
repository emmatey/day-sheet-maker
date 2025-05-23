package emmatey.gui;

import javax.sound.sampled.*;
import javax.swing.*;
import java.io.File;
import java.io.IOException;

public class MediaHandler {
    private static Clip activeClip;

    public static String locateJar() {
        try {
            String jarPath = new File(MainWindow.class
                .getProtectionDomain()
                .getCodeSource()
                .getLocation()
                .toURI()).getParent();

            // Check for IDE / workspace / temp paths like Roaming
                if (jarPath.toLowerCase().contains("roaming") || jarPath.toLowerCase().contains("workspace")) {
                String fallback = System.getProperty("user.dir");
                File parentDir = new File(fallback).getParentFile(); // navigate to folder containing java folder i.e. project folder
                String fallWayBack = parentDir.getAbsolutePath();
                System.out.println("Detected IDE environment. Falling back to working dir: " + fallWayBack);
                return fallWayBack;
            }

            System.out.println("jarPath resolved to: " + jarPath);
            return jarPath;

        } catch (Exception e) {
            e.printStackTrace();
            return System.getProperty("user.dir");  // last resort
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

    public static void playSound(String filename, boolean loop) {
        stopSound();  // stop existing audio

        try {
            String path = File.separator + locateJar() + File.separator + "assets" + File.separator + filename;
            File audioFile = new File(path);

            System.out.println("Trying to load wav from: " + audioFile.getAbsolutePath());
            System.out.println("Exists? " + audioFile.exists());

            AudioInputStream audioStream = AudioSystem.getAudioInputStream(audioFile);
            Clip audioClip = AudioSystem.getClip();
            audioClip.open(audioStream);
            activeClip = audioClip;

            if (loop) {
                activeClip.loop(Clip.LOOP_CONTINUOUSLY);
            } else {
                activeClip.start();
            }

        } catch (UnsupportedAudioFileException | IOException | LineUnavailableException e) {
            e.printStackTrace();
        }
    }

    public static JLabel getGifLabel(String filename) {
        String path = locateJar() + File.separator + "assets" + File.separator + filename;
        File gifFile = new File(path);
        System.out.println("Trying to load gif from: " + gifFile.getAbsolutePath());
        System.out.println("Exists? " + gifFile.exists());

        ImageIcon gifIcon = new ImageIcon(gifFile.getAbsolutePath());
        JLabel gifLabel = new JLabel(gifIcon);
        return gifLabel;
    }

    public static ImageIcon getGifIcon(String filename) {
        String path = locateJar() + File.separator + "assets" + File.separator + filename;
        File gifFile = new File(path);
        System.out.println("Trying to load gif from: " + gifFile.getAbsolutePath());
        System.out.println("Exists? " + gifFile.exists());

        return new ImageIcon(gifFile.getAbsolutePath());
    }
}