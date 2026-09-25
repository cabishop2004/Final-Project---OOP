# Final-Project---OOP



# Congressional Stock Trade Tracker and Alert System

## Team Information

**Course:** CSCI 375 – Object-Oriented Programming  
**Semester:** Fall 2026

**Team Members:**
- Caleb Bishop
- Eric [Last Name]

## Project Overview

This project proposes a Python application that tracks publicly disclosed stock transactions by members of the U.S. Congress and notifies users when newly reported trades match their interests.

The application aims to make congressional financial disclosures easier to access and monitor by consolidating data from external REST APIs and providing customizable transaction alerts.

## Planned Features

- Retrieve and process publicly available congressional trading disclosures.
- Search and filter trades by politician, stock, transaction type and reported value range.
- Create customizable alert rules.
- Notify users of matching transactions through email or SMS.
- Detect duplicate records and handle API errors and rate limits.
- Test application functionality using unit tests and mocked API responses.

## Object-Oriented Design

The application will use encapsulation, inheritance, polymorphism and abstraction to maintain a modular, extensible design.

The proposed architecture includes:

- **Politician:** Represents a member of Congress.
- **Stock:** Represents a publicly traded security.
- **Trade:** Stores information about a reported transaction.
- **DataProvider:** Retrieves and normalizes financial disclosure data from external APIs.
- **AlertRule:** Defines the conditions that a transaction must satisfy to trigger an alert.
- **AlertManager:** Evaluates reported transactions against configured alert rules.
- **Notifier:** Provides a common interface for notification methods, such as email and SMS.

The design will allow additional data providers and notification methods to be incorporated without substantially changing the existing application.

## Planned Technologies

- Python
- Object-oriented programming
- REST APIs
- JSON
- Python unittest and pytest
- Git and GitHub

Additional libraries and services will be selected during development.

## Limitations

Congressional trading disclosures are published after transactions occur, and reported amounts are generally provided as ranges rather than exact figures. Consequently, this application is intended as an informational tool, not a real-time trading or financial prediction system.

## Project Status

**Current phase:** Project proposal and abstract approval.

Implementation, testing and documentation will follow approval of the project proposal.
