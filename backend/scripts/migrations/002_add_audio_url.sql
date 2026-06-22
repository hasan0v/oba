-- Add audio_url column to chat_messages table
ALTER TABLE chat_messages 
ADD COLUMN IF NOT EXISTS audio_url TEXT;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_chat_messages_audio_url 
ON chat_messages (audio_url) 
WHERE audio_url IS NOT NULL;
