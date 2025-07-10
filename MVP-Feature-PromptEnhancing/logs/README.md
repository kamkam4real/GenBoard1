# Application Logs

This directory contains application logs with structured JSON format for easy analysis.

## Log Format

Each log entry contains:
- `timestamp`: ISO format timestamp
- `session_id`: Unique session identifier
- `action`: Type of action performed
- `level`: Log level (INFO, ERROR, WARNING)
- `details`: Structured data about the action
- `user_agent`: Browser/client information

## Log Types

### User Actions
- `api_key_validation`: API key validation attempts
- `mode_changed`: UI mode switches
- `chat_message_sent`: User chat inputs
- `image_generation_started`: Image generation requests
- `video_generation_started`: Video generation requests

### System Events
- `application_started`: App initialization
- `interface_rendered`: UI component rendering
- `statistics_displayed`: Usage stats shown

### API Calls
- Performance metrics for all external API calls
- Success/failure tracking
- Response time monitoring

### Errors
- Detailed error context and stack traces
- User action context when errors occur
- Recovery information

## Analysis

Use these logs for:
- Performance monitoring
- Error debugging
- User behavior analysis
- API usage tracking
- Cost optimization