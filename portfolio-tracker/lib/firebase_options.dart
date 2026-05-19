// File generated based on google-services.json
// Re-run flutterfire configure to regenerate

import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        throw UnsupportedError('iOS platform not configured.');
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyCVs6DgBwIFNA0a0BSvxkCz86MxrRfnVCs',
    appId: '1:120507805270:android:05af664fefeed5438b55f7',
    messagingSenderId: '120507805270',
    projectId: 'portfolio-tracker-d3939',
    storageBucket: 'portfolio-tracker-d3939.firebasestorage.app',
  );

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyCVs6DgBwIFNA0a0BSvxkCz86MxrRfnVCs',
    appId: '1:120507805270:web:placeholder',
    messagingSenderId: '120507805270',
    projectId: 'portfolio-tracker-d3939',
    storageBucket: 'portfolio-tracker-d3939.firebasestorage.app',
    authDomain: 'portfolio-tracker-d3939.firebaseapp.com',
  );
}
