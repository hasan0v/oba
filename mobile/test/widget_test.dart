// Basic smoke test for ObaApp.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:oba_smart_assistant/main.dart';

void main() {
  testWidgets('ObaApp builds without throwing', (WidgetTester tester) async {
    await tester.pumpWidget(const ObaApp());
    // We only assert that pumpWidget completes — full rendering needs
    // Supabase/AppConfig setup that's out of scope for this smoke test.
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
