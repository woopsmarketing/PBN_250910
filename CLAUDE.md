# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PBN (Private Blog Network) automated backlink system that combines high-quality content generation with intelligent link building. The system automatically creates SEO-optimized content and distributes it across multiple WordPress sites to build backlinks for clients.

## Development Commands

### Environment Setup
```bash
# Install base dependencies
pip install -r requirements.txt

# Install additional link system dependencies
pip install -r requirements_link_system.txt

# Install critical AI/ML dependencies
pip install sentence-transformers scikit-learn faiss-cpu numpy
```

### Testing Commands
```bash
# Test enhanced content generation system
python test_enhanced_content.py

# Test the intelligent link system
python test_link_system.py

# Test AI similarity functions
python test_ai_similarity.py

# Test PBN retry system
python test_pbn_retry_system.py

# Test environment setup
python test_enhanced_main_environment.py
```

### Running the System
```bash
# Run enhanced system (v2.0) with intelligent link building
python enhanced_main_v2.py

# Run enhanced system (v1.0) with advanced content generation
python enhanced_main.py

# Run basic system
python main.py

# Run manager interface
python manager.py
```

### Database and Utilities
```bash
# Build FAISS index for similarity search
python build_faiss_index.py

# Check crawled PBN data
python check_crawl_data.py

# Crawl PBN content for link building
python pbn_content_crawler.py

# Test content cleaning functions
python test_content_cleaning.py
```

## System Architecture

### Core Components

1. **Content Generation System** (`src/generators/content/`)
   - `advanced_content_generator.py` - Main content orchestrator
   - `title_generator.py` - SEO-optimized title generation
   - `outline_generator.py` - Structured content outlines
   - `section_generator.py` - Individual section content
   - `keyword_generator.py` - LSI and longtail keywords
   - `image_generator.py` - Image metadata generation

2. **HTML Processing** (`src/generators/html/`)
   - `simple_html_converter.py` - Converts content to WordPress HTML

3. **Database Management**
   - `controlDB.py` - Main database operations and schema
   - `controlDB.db` - SQLite database for clients, PBN sites, posts
   - `pbn_content_database.db` - Crawled PBN content for link building

4. **WordPress Integration**
   - `wordpress_functions.py` - WordPress REST API and XML-RPC operations

5. **Intelligent Link Building**
   - `intelligent_link_builder.py` - AI-powered internal link insertion
   - `improved_similarity_system.py` - FAISS-based similarity search
   - `pbn_content_crawler.py` - Crawls existing PBN content

### Data Flow

1. **Content Creation**: AI generates 1500-3000 word articles with 7-10 H2 sections
2. **Link Building**: System automatically inserts client links (100%) + internal links based on semantic similarity
3. **Distribution**: Content is posted to randomly selected PBN sites via WordPress API
4. **Tracking**: All operations logged in SQLite database

### Key Features

- **SEO-Optimized Content**: Automatic LSI keywords, meta descriptions, structured content
- **Intelligent Link Building**: AI-powered semantic similarity for internal linking
- **Batch Processing**: Handle multiple clients and campaigns simultaneously
- **Quality Control**: Automated validation of content length, keyword density, link quality
- **Retry Logic**: Robust error handling and automatic retries for failed operations

## Important Configuration

### Environment Variables (.env)
- `OPENAI_API_KEY` - Required for content generation
- `OPENAI_DALLE_API_KEY` - Required for image generation

### System Requirements
- Python 3.8+
- Minimum 4GB RAM (for AI models)
- 2GB+ free disk space (for databases and models)
- Stable internet connection (for API calls and WordPress operations)

### First-Time Setup Procedure

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_link_system.txt
   ```

2. **Initialize PBN Content Database**
   ```bash
   # Run menu option 21 in enhanced_main_v2.py
   python enhanced_main_v2.py
   # Select: 21. 🔗 PBN 콘텐츠 크롤링 (링크 데이터베이스 구축)
   ```

3. **Verify System**
   ```bash
   # Run menu option 22 to check database statistics
   # Run menu option 23 to test similarity search
   ```

## Database Schema

### Main Tables
- `clients` - Client information and campaign status
- `client_keywords` - Keywords assigned to each client
- `pbn_sites` - WordPress PBN site credentials
- `posts` - Generated posts and publishing history
- `pbn_posts` - Crawled content from PBN sites for link building

### Content Generation Workflow

The system uses a modular approach:

1. **Title Generation**: Creates multiple SEO-optimized titles with power words
2. **Outline Creation**: Generates 7-10 H2 sections based on target keywords
3. **Section Writing**: Produces detailed content for each section (200-500 words each)
4. **Keyword Integration**: Automatically inserts LSI keywords and definitions
5. **Link Building**: Uses FAISS similarity search to find relevant internal linking opportunities
6. **HTML Conversion**: Converts to WordPress-compatible HTML with proper formatting

## Quality Metrics

- **Content Length**: 1500-3000 words
- **Section Count**: 7-10 H2 sections
- **Keyword Density**: 1-3% for target keywords
- **Link Density**: Maximum 3% of total content
- **SEO Score**: Automated scoring system targeting 85/100+

## Common Issues

### Import/Module Errors
- Ensure all dependencies are installed
- Check Python path configuration
- Verify src/ directory is accessible

### AI Model Loading Issues
- First-time model download requires internet connection
- Models cached in ~/.cache/huggingface/
- Requires ~500MB RAM when loaded

### WordPress API Failures
- Verify PBN site URLs include https://
- Check WordPress REST API is enabled
- Validate credentials in database

### Database Corruption
- Run integrity checks: `PRAGMA integrity_check;`
- Backup databases before major operations
- Use transactions for batch operations

## Performance Optimization

- **Parallel Processing**: System supports concurrent operations across multiple PBN sites
- **Caching**: FAISS index provides sub-second similarity searches
- **Batch Operations**: Process multiple clients simultaneously
- **Memory Management**: Models loaded once and reused across operations