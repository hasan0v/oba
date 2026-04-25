import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;

/// Script to upload product images to Supabase Storage
/// Run with: dart run scripts/upload_product_images.dart
/// 
/// IMPORTANT: Replace SUPABASE_SERVICE_ROLE_KEY with your actual service role key
/// Get it from: Supabase Dashboard -> Settings -> API -> service_role key

const supabaseUrl = 'https://keleythlzrtmvoetixcl.supabase.co';
// Use service role key for server-side uploads (replace with your actual key)
// Get from: https://supabase.com/dashboard/project/keleythlzrtmvoetixcl/settings/api
const supabaseServiceKey = String.fromEnvironment('SUPABASE_SERVICE_KEY', 
    defaultValue: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlbGV5dGhsenJ0bXZvZXRpeGNsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTE3OTMyMywiZXhwIjoyMDg0NzU1MzIzfQ.REPLACE_WITH_REAL_SERVICE_KEY');
const bucketName = 'product-images';

Future<void> main() async {
  // Check if key is set via environment
  final serviceKey = Platform.environment['SUPABASE_SERVICE_KEY'] ?? supabaseServiceKey;
  
  if (serviceKey.contains('REPLACE_WITH_REAL')) {
    print('ERROR: Please set SUPABASE_SERVICE_KEY environment variable');
    print('');
    print('Get your service role key from:');
    print('https://supabase.com/dashboard/project/keleythlzrtmvoetixcl/settings/api');
    print('');
    print('Then run:');
    print('  \$env:SUPABASE_SERVICE_KEY="your-key-here"');
    print('  dart run scripts/upload_product_images.dart');
    exit(1);
  }
  
  final imagesDir = Directory('assets/images/products');
  
  if (!await imagesDir.exists()) {
    print('Error: Images directory not found at ${imagesDir.path}');
    exit(1);
  }
  
  final files = await imagesDir
      .list()
      .where((entity) => entity is File && entity.path.endsWith('.webp'))
      .cast<File>()
      .toList();
  
  print('Found ${files.length} product images to upload');
  print('');
  
  int uploaded = 0;
  int failed = 0;
  final List<String> failedFiles = [];
  final List<Map<String, String>> uploadedImages = [];
  
  for (final file in files) {
    final fileName = path.basename(file.path);
    // Convert filename to URL-safe format
    final safeName = fileName
        .replaceAll(' ', '_')
        .toLowerCase();
    
    try {
      final bytes = await file.readAsBytes();
      
      final response = await http.post(
        Uri.parse('$supabaseUrl/storage/v1/object/$bucketName/$safeName'),
        headers: {
          'Authorization': 'Bearer $serviceKey',
          'apikey': serviceKey,
          'Content-Type': 'image/webp',
          'x-upsert': 'true', // Overwrite if exists
        },
        body: bytes,
      );
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        uploaded++;
        final publicUrl = '$supabaseUrl/storage/v1/object/public/$bucketName/$safeName';
        uploadedImages.add({
          'original': fileName,
          'safe': safeName,
          'url': publicUrl,
        });
        print('✓ Uploaded: $fileName');
      } else {
        failed++;
        failedFiles.add(fileName);
        print('✗ Failed: $fileName (${response.statusCode}: ${response.body})');
      }
    } catch (e) {
      failed++;
      failedFiles.add(fileName);
      print('✗ Error uploading $fileName: $e');
    }
  }
  
  print('');
  print('========================================');
  print('Upload complete!');
  print('Uploaded: $uploaded');
  print('Failed: $failed');
  
  if (failedFiles.isNotEmpty) {
    print('');
    print('Failed files:');
    for (final f in failedFiles) {
      print('  - $f');
    }
  }
  
  print('');
  print('Public URL format:');
  print('$supabaseUrl/storage/v1/object/public/$bucketName/<filename>');
  
  // Generate SQL to update products table
  if (uploadedImages.isNotEmpty) {
    print('');
    print('========================================');
    print('SQL to update products image_url:');
    print('');
    for (final img in uploadedImages) {
      final productName = img['original']!.replaceAll('.webp', '');
      print("UPDATE products SET image_url = '${img['url']}' WHERE name = '$productName';");
    }
  }
}
