# CatWalk CLI Tutorial

This guide shows how to use CatWalk's command-line interface to manage workflows.

## 📋 Table of Contents

1. [Basic Commands](#basic-commands)
2. [Working with Nodes](#working-with-nodes)
3. [Working with Edges](#working-with-edges)
4. [Workflow Management](#workflow-management)
5. [Server Operations](#server-operations)
6. [Validation and Debugging](#validation-and-debugging)

## Basic Commands

### Initialize a New Workflow

```bash
# Create a new empty workflow
catwalk init my-workflow.json

# Create with a starter template
catwalk init my-workflow.json --template simple
catwalk init my-workflow.json --template reactflow
```

### Run Workflows

```bash
# Run a workflow file
catwalk run flow.json

# Run with verbose output
catwalk run flow.json --verbose

# Run and save output to file
catwalk run flow.json --output results.json
```

### Validate Workflows

```bash
# Basic validation
catwalk validate flow.json

# Validate with detailed error reporting
catwalk validate flow.json --detailed

# Validate multiple files
catwalk validate *.json
```

## Working with Nodes

### Adding Nodes

```bash
# Add a basic trigger node
catwalk add node --file flow.json \
  --id start_node \
  --type trigger \
  --name "Data Source" \
  --func "lambda ctx: {'data': [1, 2, 3, 4, 5]}"

# Add a processing node with position (ReactFlow compatible)
catwalk add node --file flow.json \
  --id process_data \
  --type extraction \
  --name "Calculate Sum" \
  --func "lambda ctx: sum(ctx['start_node']['data'])" \
  --position '{"x": 200, "y": 100}'

# Add a conditional node
catwalk add node --file flow.json \
  --id check_result \
  --type conditional \
  --name "Validate Result" \
  --func "lambda ctx: ctx['process_data'] > 0"

# Add an execution node with metadata
catwalk add node --file flow.json \
  --id output_result \
  --type execution \
  --name "Display Output" \
  --func "lambda ctx: print(f'Result: {ctx[\"process_data\"]}')" \
  --data '{"category": "output", "description": "Final result display"}'
```

### Updating Nodes

```bash
# Update node function
catwalk update node --file flow.json \
  --id process_data \
  --func "lambda ctx: sum(ctx['start_node']['data']) * 2"

# Update node name and type
catwalk update node --file flow.json \
  --id process_data \
  --name "Double Sum" \
  --type extraction

# Update node position (for ReactFlow)
catwalk update node --file flow.json \
  --id process_data \
  --position '{"x": 250, "y": 150}'

# Update multiple properties at once
catwalk update node --file flow.json \
  --id process_data \
  --name "Enhanced Calculator" \
  --func "lambda ctx: sum(ctx['start_node']['data']) ** 2" \
  --data '{"version": "2.0", "optimized": true}'
```

### Removing Nodes

```bash
# Remove a single node
catwalk remove node --file flow.json --id process_data

# Remove multiple nodes
catwalk remove node --file flow.json --id process_data,check_result

# Remove node and its connected edges automatically
catwalk remove node --file flow.json --id process_data --cascade

# Remove all nodes of a specific type
catwalk remove node --file flow.json --type conditional
```

### Listing Nodes

```bash
# List all nodes
catwalk list nodes --file flow.json

# List nodes of a specific type
catwalk list nodes --file flow.json --type trigger

# List nodes with details
catwalk list nodes --file flow.json --detailed

# List in table format
catwalk list nodes --file flow.json --format table
```

## Working with Edges

### Adding Edges

```bash
# Add a basic edge
catwalk add edge --file flow.json \
  --source start_node \
  --target process_data

# Add edge with ID (ReactFlow compatible)
catwalk add edge --file flow.json \
  --id edge_1 \
  --source start_node \
  --target process_data

# Add edge with styling
catwalk add edge --file flow.json \
  --id styled_edge \
  --source process_data \
  --target output_result \
  --style '{"stroke": "#10b981", "strokeWidth": 2}' \
  --animated true

# Add multiple edges at once
catwalk add edge --file flow.json \
  --connections "start_node->process_data,process_data->check_result,check_result->output_result"
```

### Updating Edges

```bash
# Update edge target
catwalk update edge --file flow.json \
  --id edge_1 \
  --target new_target_node

# Update edge styling
catwalk update edge --file flow.json \
  --id edge_1 \
  --style '{"stroke": "#ef4444", "strokeWidth": 3}' \
  --animated false

# Update edge using source/target (if no ID)
catwalk update edge --file flow.json \
  --source start_node \
  --target process_data \
  --new-target output_result
```

### Removing Edges

```bash
# Remove edge by ID
catwalk remove edge --file flow.json --id edge_1

# Remove edge by source/target
catwalk remove edge --file flow.json \
  --source start_node \
  --target process_data

# Remove all edges from a node
catwalk remove edge --file flow.json --from start_node

# Remove all edges to a node  
catwalk remove edge --file flow.json --to output_result

# Remove multiple edges
catwalk remove edge --file flow.json --ids edge_1,edge_2,edge_3
```

### Listing Edges

```bash
# List all edges
catwalk list edges --file flow.json

# List edges from a specific node
catwalk list edges --file flow.json --from start_node

# List edges to a specific node
catwalk list edges --file flow.json --to output_result

# List in detailed format
catwalk list edges --file flow.json --detailed
```

## Workflow Management

### Templates and Initialization

```bash
# Available templates
catwalk templates list

# Create from template
catwalk init --template data-pipeline my-pipeline.json
catwalk init --template api-workflow my-api.json
catwalk init --template ml-pipeline my-ml.json

# Save current workflow as template
catwalk template save --file flow.json --name my-custom-template
```

### Workflow Operations

```bash
# Copy workflow
catwalk copy flow.json new-flow.json

# Merge workflows
catwalk merge base-flow.json additional-nodes.json --output merged-flow.json

# Extract subworkflow
catwalk extract --file flow.json \
  --nodes start_node,process_data \
  --output sub-workflow.json

# Optimize workflow (remove unused nodes/edges)
catwalk optimize --file flow.json --output optimized-flow.json
```

### Import/Export

```bash
# Export to different formats
catwalk export --file flow.json --format yaml --output flow.yaml
catwalk export --file flow.json --format graphviz --output flow.dot
catwalk export --file flow.json --format mermaid --output flow.mmd

# Import from other formats
catwalk import --file flow.yaml --format yaml --output flow.json
catwalk import --file pipeline.yaml --format github-actions --output flow.json
```

## Server Operations

### Starting the Server

```bash
# Start server on default port (8000)
catwalk serve

# Start on custom port
catwalk serve --port 9000

# Start with specific host
catwalk serve --host 0.0.0.0 --port 8080

# Start with auto-reload (development)
catwalk serve --reload

# Start with log level
catwalk serve --log-level debug
```

### Server Management

```bash
# Check server status
catwalk status

# Stop server
catwalk stop

# Restart server
catwalk restart

# View server logs
catwalk logs

# Test server health
catwalk health-check --url http://localhost:8000
```

## Validation and Debugging

### Validation Commands

```bash
# Basic validation
catwalk validate flow.json

# Validate with schema version
catwalk validate flow.json --schema-version 1.0

# Validate and fix common issues
catwalk validate flow.json --fix --output fixed-flow.json

# Validate workflow execution without running
catwalk validate flow.json --check-execution

# Batch validation
catwalk validate workflows/*.json --summary
```

### Debugging

```bash
# Dry run (check execution path without running functions)
catwalk run flow.json --dry-run

# Debug mode (step through execution)
catwalk run flow.json --debug

# Show execution graph
catwalk graph flow.json --output graph.png

# Analyze workflow performance
catwalk analyze flow.json --metrics

# Check for circular dependencies
catwalk check flow.json --circular

# Lint workflow for best practices
catwalk lint flow.json
```

### Information Commands

```bash
# Show workflow statistics
catwalk info flow.json

# Show node/edge counts
catwalk stats flow.json

# Show workflow execution order
catwalk order flow.json

# Show dependencies for a node
catwalk deps --file flow.json --node process_data

# Show which nodes depend on a specific node
catwalk dependents --file flow.json --node start_node
```

## Advanced Usage

### Batch Operations

```bash
# Process multiple workflows
catwalk batch-run workflows/*.json --parallel

# Validate multiple files
catwalk batch-validate "workflow-*.json" --fail-fast

# Update multiple workflows
catwalk batch-update workflows/*.json \
  --add-node '{"id": "logger", "type": "execution", "name": "Log", "func": "lambda ctx: print(ctx)"}'
```

### Configuration

```bash
# Set default configuration
catwalk config set default-file flow.json
catwalk config set default-port 9000
catwalk config set auto-save true

# Show current configuration
catwalk config show

# Reset configuration
catwalk config reset
```

### Scripting and Automation

```bash
# Generate workflow from script
catwalk generate --from-script my-script.py --output generated-flow.json

# Watch file for changes and auto-validate
catwalk watch flow.json --validate

# Run workflow on file change
catwalk watch flow.json --run

# Export workflow metrics
catwalk metrics flow.json --export metrics.csv
```

## Example Workflow: Complete CLI Session

```bash
# 1. Initialize new workflow
catwalk init my-pipeline.json --template simple

# 2. Add nodes
catwalk add node --file my-pipeline.json \
  --id data_source \
  --type trigger \
  --name "Load Data" \
  --func "lambda ctx: {'numbers': [1, 2, 3, 4, 5]}"

catwalk add node --file my-pipeline.json \
  --id calculate \
  --type extraction \
  --name "Calculate Sum" \
  --func "lambda ctx: sum(ctx['data_source']['numbers'])"

catwalk add node --file my-pipeline.json \
  --id output \
  --type execution \
  --name "Show Result" \
  --func "lambda ctx: f'Sum is: {ctx[\"calculate\"]}'"

# 3. Add edges
catwalk add edge --file my-pipeline.json --source data_source --target calculate
catwalk add edge --file my-pipeline.json --source calculate --target output

# 4. Validate
catwalk validate my-pipeline.json

# 5. Run
catwalk run my-pipeline.json

# 6. Update node
catwalk update node --file my-pipeline.json \
  --id calculate \
  --func "lambda ctx: sum(ctx['data_source']['numbers']) * 2"

# 7. Run again
catwalk run my-pipeline.json

# 8. Start server
catwalk serve --port 8080 &

# 9. Test via HTTP
curl -X POST -H "Content-Type: application/json" \
  --data-binary @my-pipeline.json \
  http://localhost:8080/run
```

## Error Handling

Common errors and solutions:

```bash
# Node not found
Error: Node 'nonexistent' not found
Solution: catwalk list nodes --file flow.json

# Circular dependency
Error: Circular dependency detected: n1 -> n2 -> n1
Solution: catwalk check flow.json --circular --fix

# Invalid JSON
Error: JSON syntax error at line 15
Solution: catwalk validate flow.json --detailed

# Missing edge target
Error: Edge target 'missing_node' not found
Solution: catwalk list nodes --file flow.json
          catwalk remove edge --file flow.json --target missing_node
```

This CLI interface provides powerful tools for managing CatWalk workflows both interactively and programmatically.