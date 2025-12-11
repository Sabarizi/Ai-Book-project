# Research Document: Physical AI & Humanoid Robotics Book Implementation

## Decision: Docusaurus Version
**Rationale**: Docusaurus 3.x provides modern React-based architecture, excellent Markdown support, built-in search, and strong documentation capabilities that align with educational content needs.
**Alternatives considered**:
- Hugo: More complex for non-technical users
- Jekyll: Less modern and requires more configuration
- GitBook: Limited customization options
- Custom React site: Higher development overhead

## Decision: Content Generation Pipeline
**Rationale**: Claude CLI integrated with Speckit Plus provides automated content generation while maintaining quality through structured prompts and validation workflows.
**Alternatives considered**:
- Manual writing only: Time-intensive and inconsistent
- Other AI tools: Less integration with Speckit Plus ecosystem
- Template-based generation: Less flexibility for complex content

## Decision: Diagram Format
**Rationale**: SVG as primary format with PNG fallbacks provides scalability, accessibility, and small file sizes while maintaining compatibility across all browsers.
**Alternatives considered**:
- Only PNG: Larger file sizes, not scalable
- Only PDF: Not web-friendly for inline content
- Interactive diagrams: Higher complexity and maintenance

## Decision: Hardware Integration Approach
**Rationale**: Structured JSON BOMs with supplier links provide reproducible hardware specifications while allowing for alternative components.
**Alternatives considered**:
- Embedded purchase links: May become outdated quickly
- Static text lists: Not interactive or easily updated
- External service integration: Higher complexity and dependencies

## Decision: PDF Generation Method
**Rationale**: GitHub Actions with Puppeteer provides automated, consistent PDF generation with good formatting control.
**Alternatives considered**:
- Docusaurus static export: Limited formatting control
- Manual PDF creation: Not scalable or maintainable
- Third-party services: Additional dependencies and costs

## Decision: Accessibility Compliance Level
**Rationale**: WCAG 2.1 AA provides comprehensive accessibility while being achievable and recognized as a standard.
**Alternatives considered**:
- WCAG 2.0: Less comprehensive than 2.1
- WCAG 2.1 AAA: More stringent requirements that may limit design options
- Custom accessibility guidelines: Less recognized and harder to validate

## Decision: Multi-language Support Implementation
**Rationale**: Docusaurus built-in i18n provides standard approach with good tooling support and community resources.
**Alternatives considered**:
- Custom solution: Higher development overhead
- External service: Additional complexity and dependencies
- Single language only: Limits accessibility for international learners