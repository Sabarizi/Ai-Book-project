# Data Model: Physical AI & Humanoid Robotics Book

## Module Entity
- **id**: string (module-{number}-{topic})
- **title**: string (required)
- **summary**: string (required)
- **learningObjectives**: array of strings (3-6 items, required)
- **keyConcepts**: array of strings (required)
- **prerequisites**: string (required)
- **deliverables**: array of strings (required)
- **labActivities**: string (required)
- **expectedOutcomes**: string (required)
- **difficultyLevel**: enum (Beginner, Beginner to Intermediate, Intermediate, Intermediate to Advanced, Advanced)
- **requiredDiagrams**: array of strings (required)
- **createdAt**: datetime
- **updatedAt**: datetime

## Diagram Entity
- **id**: string (auto-generated)
- **moduleId**: string (foreign key to Module)
- **name**: string (required)
- **description**: string
- **format**: enum (SVG, PNG)
- **path**: string (required, relative to static/diagrams/)
- **altText**: string (required for accessibility)
- **createdAt**: datetime
- **updatedAt**: datetime

## CodeExample Entity
- **id**: string (auto-generated)
- **moduleId**: string (foreign key to Module)
- **title**: string (required)
- **description**: string
- **language**: string (required, e.g., Python, JavaScript)
- **code**: string (required)
- **path**: string (required, relative to code-examples/)
- **createdAt**: datetime
- **updatedAt**: datetime

## HardwareComponent Entity
- **id**: string (auto-generated)
- **name**: string (required)
- **category**: string (required, e.g., Actuator, Sensor, Controller)
- **specifications**: object (required, key-value pairs)
- **quantity**: number (required)
- **supplier**: string
- **partNumber**: string
- **cost**: number
- **link**: string (URL to purchase)
- **createdAt**: datetime
- **updatedAt**: datetime

## ModuleHardwareMapping Entity
- **moduleId**: string (foreign key to Module)
- **componentId**: string (foreign key to HardwareComponent)
- **usageDescription**: string (how the component is used in this module)
- **createdAt**: datetime

## Manifest Entity
- **id**: string (modules.json)
- **modules**: array of Module references
- **navigation**: object (sidebar structure)
- **dependencies**: object (cross-module references)
- **version**: string (semantic versioning)
- **createdAt**: datetime
- **updatedAt**: datetime

## Validation Rules
- Module.title must be 5-100 characters
- Module.learningObjectives must contain 3-6 items
- Module.difficultyLevel must be one of the defined enum values
- Diagram.altText must be provided for accessibility
- HardwareComponent.quantity must be > 0
- ModuleHardwareMapping references must exist in respective entities

## State Transitions
- Module: draft → review → published → archived
- Diagram: pending → generated → reviewed → approved → archived
- CodeExample: draft → tested → approved → deprecated
- HardwareComponent: proposed → validated → approved → discontinued