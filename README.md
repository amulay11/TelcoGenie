# TelcoGenie 2.0 - AI-Powered Telecom Customer Service Assistant

## Overview

TelcoGenie is an intelligent AI-powered customer service chatbot designed specifically for telecommunications companies. Built with Flask and OpenAI's GPT models, it provides automated customer support for mobile service queries, plan recommendations, and account management.

## Features

### 🤖 Core Capabilities
- **Prepaid Balance Enquiry**: Check prepaid mobile balance and usage details
- **Postpaid Billing Enquiry**: Retrieve billing information and due dates
- **Plan Details**: Get current subscription and plan information
- **Smart Plan Recommendations**: AI-powered plan suggestions based on usage patterns
- **Natural Language Processing**: Understand customer queries in conversational language
- **Content Moderation**: Built-in safety checks for inappropriate content

### 🎯 Supported Query Types
1. **Balance & Billing**
   - Prepaid balance checks
   - Postpaid bill inquiries
   - Payment due dates
   - Usage history

2. **Plan Management**
   - Current plan details
   - Plan change requests
   - New connection setup
   - Plan comparisons

3. **Customer Support**
   - Account information
   - Service status
   - Activation dates
   - Subscription details

## Technology Stack

### Backend
- **Flask**: Web framework for the application
- **OpenAI GPT**: AI model for natural language processing
- **Python 3.x**: Core programming language
- **Tenacity**: Retry mechanism for API calls

### Frontend
- **HTML/CSS**: Simple, responsive web interface
- **JavaScript**: Dynamic chat interface with auto-scroll

### Data Management
- **CSV Files**: Customer and plan data storage
- **Pandas**: Data manipulation and analysis

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- OpenAI API key
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Telco_Genie_2.0_Flask
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask openai tenacity pandas
   ```

4. **Configure OpenAI API**
   - Create a text file with your OpenAI API key
   - Update the path in `app.py` line 11:
   ```python
   openai.api_key = open("path/to/your/api_key.txt", "r").read().strip()
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - The chat interface will be available for interaction

## Project Structure

```
Telco_Genie_2.0_Flask/
├── app.py                 # Main Flask application
├── functions.py           # Core business logic and AI functions
├── dialogue_flow.py       # Conversation flow management
├── templates/             # HTML templates
│   ├── index_invite.html  # Main chat interface
│   ├── index_hello.html   # Welcome page
│   └── index_bye.html     # Goodbye page
├── static/                # Static assets
│   └── css/
│       └── styles.css     # Styling for the interface
├── telecom_subscribers_data.csv  # Customer database
├── plan_data.csv          # Available plans data
├── updated_plan_data.csv  # Enhanced plan information
└── TelcoGenie 1.0 System Design.docx  # System documentation
```

## Data Schema

### Customer Data (`telecom_subscribers_data.csv`)
- Mobile Number, Customer ID, Name
- Subscription Type (Prepaid/Postpaid)
- Plan details, Activation dates
- Balance information, Billing details

### Plan Data (`plan_data.csv`)
- Plan names and descriptions
- Pricing and features
- Data, Voice, SMS allowances
- OTT bundle information

## API Functions

### Core Functions
1. **`get_balance_info(mobile_number)`**
   - Retrieves prepaid balance information
   - Returns balance, usage, and recharge details

2. **`get_billing_info(mobile_number)`**
   - Fetches postpaid billing information
   - Returns bill amount, due date, and payment status

3. **`get_customer_details(mobile_number)`**
   - Provides customer account information
   - Returns plan details and subscription status

4. **`get_plan_recommendations(...)`**
   - AI-powered plan recommendations
   - Considers usage patterns and preferences

## Usage Examples

### Customer Queries
- "I want to check my prepaid balance"
- "What's my current bill amount?"
- "I need a new mobile connection"
- "Can you recommend a plan for me?"
- "What are the details of my current plan?"

### AI Response Flow
1. **Intent Recognition**: AI identifies customer intent
2. **Information Gathering**: Collects necessary details (mobile number, preferences)
3. **Function Calling**: Executes appropriate backend functions
4. **Response Generation**: Provides personalized, helpful responses

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_ENV`: Set to 'development' for debug mode

### API Configuration
- **Model**: GPT-3.5-turbo or GPT-4
- **Temperature**: 0.7 (balanced creativity and accuracy)
- **Max Tokens**: 1000 (sufficient for responses)

## Security Features

- **Content Moderation**: Automatic filtering of inappropriate content
- **Input Validation**: Sanitization of user inputs
- **Error Handling**: Graceful handling of API failures
- **Session Management**: Conversation state management

## Performance Optimization

- **Retry Mechanism**: Automatic retry for failed API calls
- **Caching**: Conversation state caching
- **Efficient Data Loading**: Optimized CSV data processing

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your OpenAI API key is valid and has sufficient credits
   - Check the file path in `app.py`

2. **Import Errors**
   - Verify all dependencies are installed
   - Check Python version compatibility

3. **Data Loading Issues**
   - Ensure CSV files are in the correct location
   - Verify file permissions

### Debug Mode
Run the application in debug mode for detailed error messages:
```python
app.run(debug=True, host="0.0.0.0")
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: Support for regional languages
- **Voice Integration**: Voice-to-text and text-to-speech
- **Advanced Analytics**: Customer behavior analysis
- **Integration APIs**: Connect with billing systems
- **Mobile App**: Native mobile application

### Technical Improvements
- **Database Integration**: Replace CSV with proper database
- **Microservices Architecture**: Scalable service design
- **Real-time Updates**: WebSocket integration
- **Advanced AI Models**: GPT-4 integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software. Please refer to the system design document for licensing information.

## Support

For technical support or questions:
- Review the system design document
- Check the troubleshooting section
- Contact the development team

## Version History

- **v2.0**: Enhanced AI capabilities, improved UI, better error handling
- **v1.0**: Initial release with basic chatbot functionality

---

**Note**: This application requires an active OpenAI API key and internet connection for AI functionality. Ensure compliance with data protection regulations when handling customer information. 