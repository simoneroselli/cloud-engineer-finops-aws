# Untagged Resources

This function is a governance-focused FinOps example for identifying spend that is not tagged according to cost allocation rules. It helps teams answer: “Which AWS services are contributing spend that cannot be assigned to a team, application, or owner?”

## Why this matters

Cost allocation is one of the foundations of FinOps. If spend is not tagged, it is hard to attribute costs, support chargebacks, and enforce accountability across teams.

## What the Lambda does

- reads the untagged spend SQL from the bundled Athena query
- executes the query across CUR data
- identifies services with untagged or partially allocated spend
- returns the non-compliant spend breakdown in JSON

## Best practices captured

- require business tags for cost allocation and accountability
- monitor untagged spend regularly, not just during month-end reviews
- report under-tagged services to the owning teams with clear numbers
- use automated checks to prevent governance drift over time

## Lambda name

`finops_untagged_spend_reporter`

## Related files

- [bin/untagged_spend.py](../bin/untagged_spend.py)
- [athena/untagged_spend.sql](../athena/untagged_spend.sql)
- [terraform/main.tf](../terraform/main.tf)
