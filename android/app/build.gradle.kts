plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "vn.handwriting.line"
    compileSdk = 35

    defaultConfig {
        applicationId = "vn.handwriting.line"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1"
    }

    buildTypes {
        debug {
            // Thêm x86_64 để chạy thử trên máy ảo.
            ndk { abiFilters += listOf("arm64-v8a", "x86_64") }
        }
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
            ndk { abiFilters += listOf("arm64-v8a") }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }

    androidResources { noCompress += listOf("tflite", "bin") }
    testOptions { unitTests.isReturnDefaultValues = true }
}

dependencies {
    implementation("com.google.ai.edge.litert:litert:1.4.0")
    testImplementation("junit:junit:4.13.2")
}
