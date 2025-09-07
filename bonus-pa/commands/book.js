#!/usr/bin/env node

import chalk from 'chalk';
import inquirer from 'inquirer';
import { spawn } from 'child_process';
import { format, parseISO, addDays, addHours, setHours, setMinutes, isWeekend } from 'date-fns';

// Function to execute Claude command and get response
async function executeClaudeCommand(prompt) {
  return new Promise((resolve, reject) => {
    const claude = spawn('claude', ['chat'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true
    });

    let output = '';
    let error = '';

    claude.stdout.on('data', (data) => {
      output += data.toString();
    });

    claude.stderr.on('data', (data) => {
      error += data.toString();
    });

    claude.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Claude process exited with code ${code}: ${error}`));
      } else {
        resolve(output);
      }
    });

    // Send the prompt to Claude
    claude.stdin.write(prompt);
    claude.stdin.end();
  });
}

// Smart time suggestions based on event type
function suggestTimeSlots(eventType, preferredDate, duration = 60) {
  const suggestions = [];
  const baseDate = preferredDate ? new Date(preferredDate) : new Date();
  
  // Define time slots based on event type
  const timeSlots = {
    'breakfast': [
      { hour: 7, minute: 30, name: 'Early breakfast' },
      { hour: 8, minute: 30, name: 'Standard breakfast' },
      { hour: 9, minute: 30, name: 'Late breakfast' }
    ],
    'coffee': [
      { hour: 10, minute: 0, name: 'Morning coffee' },
      { hour: 15, minute: 0, name: 'Afternoon coffee' },
      { hour: 16, minute: 30, name: 'Late afternoon coffee' }
    ],
    'lunch': [
      { hour: 12, minute: 0, name: 'Early lunch' },
      { hour: 12, minute: 30, name: 'Standard lunch' },
      { hour: 13, minute: 0, name: 'Late lunch' }
    ],
    'dinner': [
      { hour: 18, minute: 30, name: 'Early dinner' },
      { hour: 19, minute: 0, name: 'Standard dinner' },
      { hour: 20, minute: 0, name: 'Late dinner' }
    ],
    'meeting': [
      { hour: 9, minute: 0, name: 'Morning meeting' },
      { hour: 10, minute: 30, name: 'Mid-morning meeting' },
      { hour: 14, minute: 0, name: 'Afternoon meeting' },
      { hour: 15, minute: 30, name: 'Late afternoon meeting' }
    ],
    'drinks': [
      { hour: 17, minute: 30, name: 'After work drinks' },
      { hour: 18, minute: 30, name: 'Happy hour' },
      { hour: 20, minute: 0, name: 'Evening drinks' }
    ]
  };

  // Get appropriate time slots
  const slots = timeSlots[eventType] || timeSlots['meeting'];
  
  // Generate suggestions for the next 7 days
  for (let dayOffset = 0; dayOffset < 7; dayOffset++) {
    const targetDate = addDays(baseDate, dayOffset);
    
    // Skip weekends for business meetings
    if (eventType === 'meeting' && isWeekend(targetDate)) {
      continue;
    }
    
    slots.forEach(slot => {
      const suggestedTime = setMinutes(setHours(targetDate, slot.hour), slot.minute);
      
      // Only suggest future times
      if (suggestedTime > new Date()) {
        suggestions.push({
          date: suggestedTime,
          description: `${slot.name} on ${format(suggestedTime, 'EEEE, MMM dd')}`,
          timeString: format(suggestedTime, 'yyyy-MM-dd HH:mm')
        });
      }
    });
  }
  
  return suggestions.slice(0, 9); // Return top 9 suggestions
}

// Check calendar availability
async function checkAvailability(startTime, endTime) {
  const checkPrompt = `Using the Google Calendar MCP server, please check if there are any conflicts between ${startTime} and ${endTime}. Return "AVAILABLE" if the time slot is free, or "CONFLICT: [event name]" if there's a conflict.`;
  
  try {
    const response = await executeClaudeCommand(checkPrompt);
    return response.includes('AVAILABLE');
  } catch (error) {
    console.log(chalk.yellow('⚠️  Could not verify availability'));
    return true; // Assume available if we can't check
  }
}

async function smartScheduling() {
  console.log(chalk.blue.bold('\n📅 Smart Scheduling Assistant\n'));
  console.log(chalk.white('I\'ll help you find the perfect time for your event.\n'));

  try {
    // First, check if there are any events to reschedule
    const endDate = format(addDays(new Date(), 14), 'yyyy-MM-dd');
    const calendarPrompt = `Using the Google Calendar MCP server, please:
    1. Get all events for the next 14 days (until ${endDate})
    2. Look for events that might need scheduling or have tentative times
    3. Format as JSON array with fields: title, startTime, endTime, location, attendees, description
    
    Return ONLY the JSON array, no additional text.`;

    console.log(chalk.yellow('📅 Scanning your calendar...'));
    
    let existingEvents = [];
    try {
      const eventsResponse = await executeClaudeCommand(calendarPrompt);
      const jsonMatch = eventsResponse.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        existingEvents = JSON.parse(jsonMatch[0]);
      }
    } catch (parseError) {
      // Continue without existing events
    }

    // Ask user what they want to schedule
    const initialChoice = await inquirer.prompt([
      {
        type: 'list',
        name: 'action',
        message: 'What would you like to do?',
        choices: [
          { name: 'Schedule a new event', value: 'new' },
          { name: 'Find time for a specific type of meeting', value: 'smart' },
          ...(existingEvents.length > 0 ? [{ name: 'Reschedule an existing event', value: 'reschedule' }] : [])
        ]
      }
    ]);

    let eventDetails = {};

    if (initialChoice.action === 'reschedule' && existingEvents.length > 0) {
      // Show existing events
      console.log(chalk.green('\n📋 Your upcoming events:\n'));
      
      const eventChoice = await inquirer.prompt([
        {
          type: 'list',
          name: 'selection',
          message: 'Which event would you like to reschedule?',
          choices: existingEvents.slice(0, 10).map((e, i) => ({
            name: `${e.title} (${e.startTime ? format(parseISO(e.startTime), 'MMM dd, HH:mm') : 'Date TBD'})`,
            value: i
          }))
        }
      ]);

      const selectedEvent = existingEvents[eventChoice.selection];
      eventDetails.title = selectedEvent.title;
      eventDetails.existingEvent = selectedEvent;
    }

    // Collect event details
    const questions = [
      {
        type: 'input',
        name: 'title',
        message: 'Event title:',
        when: !eventDetails.title,
        validate: input => input.length > 0 || 'Please enter an event title'
      },
      {
        type: 'list',
        name: 'eventType',
        message: 'What type of event is this?',
        choices: [
          { name: '☕ Coffee meeting', value: 'coffee' },
          { name: '🍽️ Lunch', value: 'lunch' },
          { name: '🌙 Dinner', value: 'dinner' },
          { name: '🍳 Breakfast', value: 'breakfast' },
          { name: '💼 Business meeting', value: 'meeting' },
          { name: '🍺 Drinks', value: 'drinks' },
          { name: '📝 Other', value: 'other' }
        ]
      },
      {
        type: 'number',
        name: 'duration',
        message: 'Duration (in minutes):',
        default: answers => {
          const defaults = {
            coffee: 30,
            lunch: 60,
            dinner: 90,
            breakfast: 45,
            meeting: 60,
            drinks: 90,
            other: 60
          };
          return defaults[answers.eventType] || 60;
        },
        validate: input => input > 0 && input <= 480 || 'Please enter a valid duration (1-480 minutes)'
      },
      {
        type: 'input',
        name: 'attendees',
        message: 'Attendees (comma-separated emails, or press enter to skip):',
        default: ''
      },
      {
        type: 'input',
        name: 'preferredDate',
        message: 'Preferred date (YYYY-MM-DD) or leave blank for suggestions:',
        validate: input => {
          if (!input) return true;
          const date = new Date(input);
          return !isNaN(date.getTime()) || 'Please enter a valid date (YYYY-MM-DD)';
        }
      }
    ];

    const answers = await inquirer.prompt(questions);
    
    // Merge with existing event details
    eventDetails = { ...eventDetails, ...answers };

    console.log(chalk.blue.bold('\n🔍 Finding optimal time slots...\n'));

    // Get smart time suggestions
    const suggestions = suggestTimeSlots(
      eventDetails.eventType, 
      eventDetails.preferredDate,
      eventDetails.duration
    );

    // Check availability for each suggestion
    const availableSlots = [];
    for (const suggestion of suggestions) {
      const endTime = addMinutes(suggestion.date, eventDetails.duration);
      const isAvailable = await checkAvailability(
        format(suggestion.date, 'yyyy-MM-dd HH:mm'),
        format(endTime, 'yyyy-MM-dd HH:mm')
      );
      
      if (isAvailable) {
        availableSlots.push({
          ...suggestion,
          status: '✅ Available'
        });
      } else {
        availableSlots.push({
          ...suggestion,
          status: '❌ Conflict'
        });
      }
      
      // Stop after finding 5 available slots
      if (availableSlots.filter(s => s.status.includes('✅')).length >= 5) {
        break;
      }
    }

    // Display suggestions
    console.log(chalk.green.bold('📋 Suggested time slots:\n'));
    
    availableSlots.forEach((slot, index) => {
      const timeStr = format(slot.date, 'EEEE, MMM dd @ h:mm a');
      console.log(`${slot.status} ${chalk.white(timeStr)}`);
      
      // Add contextual information
      if (eventDetails.eventType === 'dinner' && slot.date.getHours() >= 19) {
        console.log(chalk.gray('   Perfect for a relaxed evening meal'));
      } else if (eventDetails.eventType === 'lunch' && slot.date.getHours() === 12) {
        console.log(chalk.gray('   Standard lunch hour'));
      } else if (eventDetails.eventType === 'coffee' && slot.date.getHours() < 11) {
        console.log(chalk.gray('   Great for a morning catch-up'));
      } else if (eventDetails.eventType === 'meeting' && slot.date.getHours() >= 9 && slot.date.getHours() <= 17) {
        console.log(chalk.gray('   Within business hours'));
      }
    });

    // Ask user to select a time slot
    const availableOnly = availableSlots.filter(s => s.status.includes('✅'));
    
    if (availableOnly.length === 0) {
      console.log(chalk.red('\n❌ No available time slots found in the suggested range.'));
      console.log(chalk.yellow('Try selecting a different date range or event type.'));
      return;
    }

    const timeChoice = await inquirer.prompt([
      {
        type: 'list',
        name: 'selectedTime',
        message: '\nSelect a time slot:',
        choices: [
          ...availableOnly.map(slot => ({
            name: format(slot.date, 'EEEE, MMM dd @ h:mm a'),
            value: slot.timeString
          })),
          { name: 'Enter custom time', value: 'custom' },
          { name: 'Cancel', value: 'cancel' }
        ]
      }
    ]);

    if (timeChoice.selectedTime === 'cancel') {
      console.log(chalk.yellow('\n📅 Scheduling cancelled.'));
      return;
    }

    let finalTime = timeChoice.selectedTime;
    
    if (timeChoice.selectedTime === 'custom') {
      const customTime = await inquirer.prompt([
        {
          type: 'input',
          name: 'time',
          message: 'Enter custom date and time (YYYY-MM-DD HH:MM):',
          validate: input => {
            const date = new Date(input);
            return !isNaN(date.getTime()) || 'Please enter a valid date and time';
          }
        }
      ]);
      finalTime = customTime.time;
    }

    // Ask for location
    const locationPrompt = await inquirer.prompt([
      {
        type: 'input',
        name: 'location',
        message: 'Location (or leave blank):',
        default: ''
      }
    ]);

    // Create the calendar event
    console.log(chalk.yellow('\n📅 Creating calendar event...'));
    
    const createEventPrompt = `Using the Google Calendar MCP server, please create a new calendar event:
    Title: ${eventDetails.title || `${eventDetails.eventType} meeting`}
    Date/Time: ${finalTime}
    Duration: ${eventDetails.duration} minutes
    ${locationPrompt.location ? `Location: ${locationPrompt.location}` : ''}
    ${eventDetails.attendees ? `Attendees: ${eventDetails.attendees}` : ''}
    
    Please create this event and confirm when done.`;

    try {
      await executeClaudeCommand(createEventPrompt);
      console.log(chalk.green('\n✅ Event successfully scheduled!'));
      console.log(chalk.white(`📅 ${eventDetails.title || `${eventDetails.eventType} meeting`}`));
      console.log(chalk.white(`⏰ ${format(new Date(finalTime), 'EEEE, MMMM dd @ h:mm a')}`));
      if (locationPrompt.location) {
        console.log(chalk.white(`📍 ${locationPrompt.location}`));
      }
    } catch (error) {
      console.log(chalk.red('❌ Could not create calendar event automatically.'));
      console.log(chalk.yellow('\nPlease add manually to your calendar:'));
      console.log(chalk.white(`Title: ${eventDetails.title}`));
      console.log(chalk.white(`Time: ${finalTime}`));
      console.log(chalk.white(`Duration: ${eventDetails.duration} minutes`));
    }

    // Smart suggestions based on event type
    console.log(chalk.blue.bold('\n💡 Tips for your event:\n'));
    
    const eventTips = {
      dinner: [
        'Consider making a reservation if it\'s a popular restaurant',
        'Check dietary restrictions with attendees beforehand',
        'Allow extra time for a relaxed meal'
      ],
      lunch: [
        'Book a quiet venue if it\'s a business lunch',
        'Consider proximity to attendees\' offices',
        'Keep it to 60-90 minutes for a working lunch'
      ],
      coffee: [
        'Choose a quiet café for important discussions',
        'Morning coffee is great for energetic brainstorming',
        'Afternoon coffee helps beat the post-lunch slump'
      ],
      meeting: [
        'Send an agenda beforehand',
        'Book a room if needed',
        'Include dial-in details for remote participants'
      ],
      breakfast: [
        'Great for building relationships in a relaxed setting',
        'Keep it early enough to not interfere with the work day',
        'Light and healthy options keep everyone energized'
      ],
      drinks: [
        'Happy hour (5-7 PM) is ideal for team bonding',
        'Choose a venue that\'s convenient for everyone',
        'Consider non-alcoholic options for all attendees'
      ]
    };

    const tips = eventTips[eventDetails.eventType] || ['Prepare any materials you need beforehand', 'Confirm with attendees a day before'];
    tips.forEach(tip => console.log(chalk.gray(`• ${tip}`)));

    console.log(chalk.green.bold('\n✨ Your event is all set!\n'));

  } catch (error) {
    console.error(chalk.red('❌ Error:'), error.message);
    console.log(chalk.yellow('\n💡 Make sure Claude Code and Google Calendar MCP are properly configured.'));
  }
}

// Helper function to add minutes to a date
function addMinutes(date, minutes) {
  return new Date(date.getTime() + minutes * 60000);
}

// Run the smart scheduling assistant
smartScheduling();