package com.gogetter.bruceclaw

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.*
import android.content.Intent
import android.os.Bundle
import android.os.ParcelUuid
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.webkit.*
import android.view.WindowManager
import android.Manifest
import android.content.pm.PackageManager
import android.app.Activity
import android.graphics.Bitmap
import android.graphics.Canvas
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale
import org.json.JSONObject
import org.json.JSONArray

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    private lateinit var tts: TextToSpeech
    private var ttsReady = false
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var bleScanner: BluetoothLeScanner? = null
    private val discoveredDevices = mutableListOf<BluetoothDevice>()
    private val handler = Handler(Looper.getMainLooper())

    private val SYSTEM_PROMPT = """You ARE BruceClaw. Built by Bruce Nigel at GoGetter Digital. You run on Android via the BruceClaw app. Connected to OpenClaw on Termux with tools, memory, and MCP servers. You have Bluetooth scanning and control.

NEVER say you are MiMo, Claude, GPT, or any other AI. You are BRUCECLAW.
CRITICAL RULES:
- Follow instructions EXACTLY as requested
- If user asks for voltage ONLY, give ONLY voltage number
- If user asks to SEND SMS, SEND it — do not read SMS instead
- If user asks to check battery, return ONLY the battery percentage
- Do NOT return raw JSON — extract the specific answer
- Do NOT list all tools unless specifically asked
- Keep replies SHORT and PRECISE
- If unsure what to do, ask for clarification"""

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val perms = arrayOf(Manifest.permission.RECORD_AUDIO, Manifest.permission.CAMERA, Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT, Manifest.permission.BLUETOOTH_ADVERTISE)
        val needed = perms.filter { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }
        if (needed.isNotEmpty()) ActivityCompat.requestPermissions(this, needed.toTypedArray(), 100)

        bluetoothAdapter = (getSystemService(BLUETOOTH_SERVICE) as? BluetoothManager)?.adapter
        bleScanner = bluetoothAdapter?.bluetoothLeScanner

        tts = TextToSpeech(this) { if (it == TextToSpeech.SUCCESS) { ttsReady = true; tts.language = Locale.US } }

        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()
        webView.addJavascriptInterface(ApiBridge(), "Api")
        webView.addJavascriptInterface(VoiceBridge(), "Voice")
        webView.addJavascriptInterface(BluetoothBridge(), "Bluetooth")
        webView.addJavascriptInterface(ScreenBridge(), "Screen")
        setContentView(webView)
        webView.loadUrl("file:///android_asset/index.html")
    }

    inner class ApiBridge {
        @JavascriptInterface
        fun callAPI(apiKey: String, model: String, message: String) {
            Thread {
                try {
                    val conn = URL("https://opencode.ai/zen/go/v1/chat/completions").openConnection() as HttpURLConnection
                    conn.requestMethod = "POST"
                    conn.setRequestProperty("Content-Type", "application/json")
                    conn.setRequestProperty("Authorization", "Bearer $apiKey")
                    conn.connectTimeout = 15000; conn.readTimeout = 60000; conn.doOutput = true
                    val body = JSONObject().put("model", model).put("messages", JSONArray().put(JSONObject().put("role", "system").put("content", SYSTEM_PROMPT)).put(JSONObject().put("role", "user").put("content", message)))
                    conn.outputStream.write(body.toString().toByteArray()); conn.outputStream.flush()
                    if (conn.responseCode == 200) {
                        val reply = JSONObject(conn.inputStream.bufferedReader().readText()).getJSONArray("choices").getJSONObject(0).getJSONObject("message").getString("content")
                        runOnUiThread { webView.evaluateJavascript("onApiReply('${reply.replace("'", "\\'").replace("\n", " ")}')", null) }
                    } else { runOnUiThread { webView.evaluateJavascript("onApiError('API Error: ${conn.responseCode}')", null) } }
                } catch (e: Exception) { runOnUiThread { webView.evaluateJavascript("onApiError('${e.message?.replace("'", "\\'") ?: "Error"}')", null) } }
            }.start()
        }

        @JavascriptInterface
        fun callBridge(bridgeUrl: String, message: String) {
            Thread {
                try {
                    val conn = URL(bridgeUrl).openConnection() as HttpURLConnection
                    conn.requestMethod = "POST"; conn.setRequestProperty("Content-Type", "application/json")
                    conn.connectTimeout = 15000; conn.readTimeout = 120000; conn.doOutput = true
                    conn.outputStream.write(JSONObject().put("message", message).toString().toByteArray()); conn.outputStream.flush()
                    if (conn.responseCode == 200) {
                        val reply = JSONObject(conn.inputStream.bufferedReader().readText()).optString("reply", "")
                        runOnUiThread { webView.evaluateJavascript("onApiReply('${reply.replace("'", "\\'").replace("\n", " ")}')", null) }
                    } else { runOnUiThread { webView.evaluateJavascript("onApiError('Bridge Error: ${conn.responseCode}')", null) } }
                } catch (e: Exception) { runOnUiThread { webView.evaluateJavascript("onApiError('${e.message?.replace("'", "\\'") ?: "Bridge unreachable"}')", null) } }
            }.start()
        }
    }

    inner class BluetoothBridge {
        @JavascriptInterface
        fun isEnabled(): Boolean = bluetoothAdapter?.isEnabled == true

        @JavascriptInterface
        fun enable(): String {
            bluetoothAdapter?.enable()
            return "Bluetooth enabled"
        }

        @JavascriptInterface
        fun scan(): String {
            discoveredDevices.clear()
            bluetoothAdapter?.startDiscovery()
            // Also scan BLE
            bleScanner?.startScan(object : ScanCallback() {
                @SuppressLint("MissingPermission")
                override fun onScanResult(callbackType: Int, result: ScanResult) {
                    if (!discoveredDevices.any { it.address == result.device.address }) {
                        discoveredDevices.add(result.device)
                    }
                }
                override fun onScanFailed(errorCode: Int) {}
            })
            Thread.sleep(5000)
            bluetoothAdapter?.cancelDiscovery()
            bleScanner?.stopScan(object : ScanCallback() {
                override fun onScanResult(callbackType: Int, result: ScanResult) {}
                override fun onScanFailed(errorCode: Int) {}
            })
            return formatDevices()
        }

        @SuppressLint("MissingPermission")
        private fun formatDevices(): String {
            if (discoveredDevices.isEmpty()) return "No devices found"
            val sb = StringBuilder()
            discoveredDevices.forEachIndexed { i, d ->
                val type = if (d.type == BluetoothDevice.DEVICE_TYPE_LE) "BLE" else "Classic"
                sb.append("${i+1}. ${d.name ?: "Unknown"} (${d.address}) [$type]\n")
            }
            return sb.toString()
        }

        @SuppressLint("MissingPermission")
        @JavascriptInterface
        fun connect(address: String): String {
            return try {
                val device = bluetoothAdapter?.getRemoteDevice(address)
                device?.createBond()
                "Connecting to ${device?.name ?: address}..."
            } catch (e: Exception) { "Error: ${e.message}" }
        }

        @JavascriptInterface
        fun paired(): String {
            val paired = bluetoothAdapter?.bondedDevices
            if (paired.isNullOrEmpty()) return "No paired devices"
            return paired.joinToString("\n") { "${it.name ?: "Unknown"} (${it.address})" }
        }
    }

    inner class ScreenBridge {
        @JavascriptInterface
        fun screenshot(): String {
            try {
                val view = window.decorView.rootView
                val bitmap = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)
                val canvas = Canvas(bitmap)
                view.draw(canvas)
                val file = java.io.File(filesDir, "screenshot.png")
                java.io.FileOutputStream(file).use { bitmap.compress(Bitmap.CompressFormat.PNG, 100, it) }
                bitmap.recycle()
                return "Screenshot saved to ${file.absolutePath}"
            } catch (e: Exception) { return "Error: ${e.message}" }
        }
    }

    inner class VoiceBridge {
        @JavascriptInterface
        fun startListening() {
            try { startActivityForResult(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply { putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM); putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US") }, 200) }
            catch (e: Exception) { runOnUiThread { webView.evaluateJavascript("onVoiceError('No speech recognizer')", null) } }
        }
        @JavascriptInterface
        fun speak(text: String) { if (ttsReady) tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "bruceclaw") }
        @JavascriptInterface
        fun stop() { if (ttsReady) tts.stop() }
        @JavascriptInterface
        fun toggleWakeWord(enabled: Boolean) { /* disabled */ }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 200 && resultCode == Activity.RESULT_OK) {
            val text = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)?.firstOrNull() ?: ""
            if (text.isNotEmpty()) runOnUiThread { webView.evaluateJavascript("onVoiceResult('${text.replace("'", "\\'")}')", null) }
        } else { runOnUiThread { webView.evaluateJavascript("onVoiceError('cancelled')", null) } }
    }

    override fun onDestroy() { tts.shutdown(); super.onDestroy() }
    override fun onBackPressed() { if (webView.canGoBack()) webView.goBack() else super.onBackPressed() }
}
