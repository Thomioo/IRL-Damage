package com.tomesh.mixin;

import com.tomesh.IRLDamageConfig;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.damage.DamageSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.net.HttpURLConnection;
import java.net.URL;

@Mixin(PlayerEntity.class)
public class PlayerEntityMixin {
    @Inject(method = "damage", at = @At("HEAD"))
    private void onDamage(DamageSource source, float amount, CallbackInfoReturnable<Boolean> cir) {
        if (!IRLDamageConfig.enabled)
            return;
        // Calculate time in seconds based on hearts (1 heart = 2 damage)
        float hearts = amount / 2.0f;
        float time;
        if (hearts < 3.0f) {
            time = 0.5f;
        } else {
            // Scale linearly: 3 hearts = 0.5s, 10 hearts = 2s
            float scale = (2.0f - 0.5f) / (10.0f - 3.0f);
            time = 0.5f + (hearts - 3.0f) * scale;
            if (time > 2.0f)
                time = 2.0f;
        }
        if (time <= 0)
            return;
        String urlString = "http://" + IRLDamageConfig.url + ":" + IRLDamageConfig.port + "/damage?time=" + time;
        // Send HTTP request asynchronously
        new Thread(() -> {
            try {
                @SuppressWarnings("deprecation")
                URL url = new URL(urlString); // Suppress deprecation warning
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(1000);
                conn.setReadTimeout(1000);
                conn.getResponseCode();
                conn.disconnect();
            } catch (Exception ignored) {
            }
        }).start();
    }

    @Inject(method = "onDeath", at = @At("HEAD"))
    private void onDeath(DamageSource source, CallbackInfo ci) {
        if (!IRLDamageConfig.enabled)
            return;
        String urlString = "http://" + IRLDamageConfig.url + ":" + IRLDamageConfig.port + "/damage?time="
                + IRLDamageConfig.maxTime;
        new Thread(() -> {
            try {
                @SuppressWarnings("deprecation")
                URL url = new URL(urlString);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(1000);
                conn.setReadTimeout(1000);
                conn.getResponseCode();
                conn.disconnect();
            } catch (Exception ignored) {
            }
        }).start();
    }
}
