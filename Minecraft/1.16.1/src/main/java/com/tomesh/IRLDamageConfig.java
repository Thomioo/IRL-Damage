package com.tomesh;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class IRLDamageConfig {
    public static boolean enabled = true;
    public static String url = "192.168.2.101";
    public static int port = 8000;
    public static float minTime = 0.5f;
    public static float maxTime = 2.0f;
    public static float minHearts = 3.0f;
    public static float maxHearts = 10.0f;

    private static final String CONFIG_FILE = "config/irl-damage.json";
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    public static void load() {
        File file = new File(CONFIG_FILE);
        if (file.exists()) {
            try (FileReader reader = new FileReader(file)) {
                IRLDamageConfig loaded = GSON.fromJson(reader, IRLDamageConfig.class);
                IRLDamageConfig.enabled = loaded.enabled;
                IRLDamageConfig.url = loaded.url;
                IRLDamageConfig.port = loaded.port;
                IRLDamageConfig.minTime = loaded.minTime;
                IRLDamageConfig.maxTime = loaded.maxTime;
                IRLDamageConfig.minHearts = loaded.minHearts;
                IRLDamageConfig.maxHearts = loaded.maxHearts;
            } catch (IOException ignored) {
            }
        } else {
            save();
        }
    }

    public static void save() {
        File file = new File(CONFIG_FILE);
        file.getParentFile().mkdirs();
        try (FileWriter writer = new FileWriter(file)) {
            GSON.toJson(new IRLDamageConfig(), writer);
        } catch (IOException ignored) {
        }
    }
}
