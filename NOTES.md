# Data Processing – Design Decisions

## 1. Deduplication

The following deduplication rules have been implemented:

- **Exact duplicates:** If two or more lines are exactly identical, only one is kept.
- **Same `event_id`:** If two or more lines share the same `event_id`, the line(s) with the lowest `ts` value are deleted.
- **Same `event_id` and `ts`:** If two or more lines share both the same `event_id` and `ts`, any fields with conflicting values are set to `null`.

## 2. Reject vs. Repair

Three rules have been implemented for rejecting records:

- **Duplication:** As explained above, keeping two or more identical records provides no additional value and unnecessarily increases storage requirements.
- **Invalid price:** If the price of an `IMPRESSION` event cannot be parsed using one of the specified formats, or if its value is less than or equal to zero, the record is rejected. This was an explicit requirement.
- **Invalid timestamp:** If the timestamp cannot be parsed using one of the specified formats, or falls outside the provided date range, the event is considered unreliable and rejected.

## 3. Scalability

- Given the large volume of events, I would use a distributed processing engine such as **Apache Spark**, reading data directly from S3.
- I would also process the data in batches, partitioned according to the date and time when the files landed in S3.

## 4. Monitoring

I would monitor the number and percentage of processing failures, both overall and for each rejection category.

Alerts would be triggered whenever these metrics exceed predefined thresholds.

## 5. AI Assistance

**Claude Code** (Sonnet 5 and Opus 5.5 models) was used during the development process.

The main purpose was to establish the project structure and develop the code responsible for data cleaning, transformation, and output generation, following specific rules and instructions. This code includes tests.

During the initial development phase, the platform experienced some issues, which required opening a new session. This explains why there are two text files containing AI conversations.