package com.medeia.android.player

/**
 * Contrato comum para os motores de reprodução.
 * Implementações Media3 e LibVLC serão adicionadas após validar o APK base.
 */
interface PlaybackEngine {
    val engineName: String
    fun release()
}

enum class PlaybackFailure {
    NETWORK,
    UNSUPPORTED_FORMAT,
    UNSUPPORTED_CODEC,
    TIMEOUT,
    AUTH_REQUIRED,
    DRM_RESTRICTED,
    SOURCE_UNAVAILABLE,
    UNKNOWN
}
