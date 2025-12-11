# Quickstart Guide: Physical AI & Humanoid Robotics Book Development

## Prerequisites
- Node.js 18+ installed
- Git installed
- Claude CLI installed and configured
- Speckit Plus installed and configured
- Basic familiarity with Markdown and JSON

## Setup Local Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Install Speckit Plus and Claude CLI** (if not already installed)
   ```bash
   # Follow installation instructions for your platform
   # Ensure both tools are in your PATH
   ```

4. **Verify installations**
   ```bash
   # Check if required tools are available
   node --version
   npm --version
   claude --version
   # Check Speckit Plus availability
   ```

## Initialize Docusaurus Project

1. **Create the Docusaurus site**
   ```bash
   npx create-docusaurus@latest website classic
   cd website
   ```

2. **Install additional dependencies**
   ```bash
   npm install @docusaurus/module-type-aliases @docusaurus/types
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## Repository Structure Setup

Create the following directory structure:

```
docs/
├── modules/
├── assets/
├── hardware/
└── manifest/
static/
├── diagrams/
├── images/
└── videos/
code-examples/
manifest/
src/
├── components/
├── pages/
└── css/
```

## Content Generation Workflow

1. **Generate module content using Claude CLI**
   ```bash
   claude generate --prompt "Create content for module X: [module details]" --output docs/modules/module-X-topic/module-X-topic.md
   ```

2. **Process content through Speckit Plus**
   ```bash
   # Run Speckit workflow to process and validate content
   specify process --config .specify/config/module-content.yaml
   ```

3. **Validate and format content**
   ```bash
   # Run linting and validation
   npm run lint
   npm run validate
   ```

## Diagram Generation

1. **Generate diagrams using automation tools**
   ```bash
   # Example command for generating diagrams
   npm run generate-diagrams -- --module 1 --type kinematic-chain
   ```

2. **Add diagrams to appropriate module folders**
   ```bash
   # Diagrams are automatically placed in static/diagrams/
   # And referenced in module markdown files
   ```

## Hardware Integration

1. **Add hardware components to manifest**
   ```json
   {
     "components": [
       {
         "id": "servo-motor-sg90",
         "name": "SG90 Servo Motor",
         "category": "Actuator",
         "specifications": {
           "torque": "1.8kg/cm",
           "speed": "0.12s/60°"
         }
       }
     ]
   }
   ```

2. **Link hardware to modules**
   ```json
   {
     "moduleId": "module-02-humanoid-mechanical-structure",
     "components": ["servo-motor-sg90", "microcontroller-arduino"]
   }
   ```

## Build and Deployment

1. **Build the site**
   ```bash
   npm run build
   ```

2. **Test the build locally**
   ```bash
   npm run serve
   ```

3. **Deploy to production** (using GitHub Actions or your preferred method)
   ```bash
   # Deployment is typically handled by CI/CD pipeline
   # See .github/workflows/deploy.yml for configuration
   ```

## Quality Assurance Commands

1. **Run all tests**
   ```bash
   npm run test
   ```

2. **Check for broken links**
   ```bash
   npm run check-links
   ```

3. **Validate accessibility**
   ```bash
   npm run a11y-check
   ```

4. **Lint all content**
   ```bash
   npm run lint-all
   ```

## Common Tasks

1. **Add a new module**
   - Create new folder in `docs/modules/`
   - Add markdown file with proper frontmatter
   - Update `sidebars.js` to include the new module
   - Add to `manifest/modules.json`

2. **Update existing content**
   - Edit the appropriate markdown file
   - Run validation commands
   - Test locally before committing

3. **Add new diagrams**
   - Generate SVG/PNG files
   - Place in appropriate directories
   - Reference in markdown files with proper alt text