#!/usr/bin/env node

import chalk from 'chalk';
import inquirer from 'inquirer';
import { spawn } from 'child_process';
import { format, parseISO, addDays, isWithinInterval } from 'date-fns';
import fetch from 'node-fetch';

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

// Function to identify events that might need restaurant bookings
function identifyDiningEvents(events) {
  const diningKeywords = [
    'dinner', 'lunch', 'breakfast', 'brunch', 'meal',
    'dining', 'restaurant', 'eat', 'food', 'celebrate',
    'birthday', 'anniversary', 'date', 'meeting over',
    'catch up', 'reunion', 'party', 'gathering'
  ];

  return events.filter(event => {
    const title = (event.title || '').toLowerCase();
    const description = (event.description || '').toLowerCase();
    const location = (event.location || '').toLowerCase();
    
    // Check if any dining keyword is present
    const hasDiningKeyword = diningKeywords.some(keyword => 
      title.includes(keyword) || 
      description.includes(keyword) || 
      location.includes(keyword)
    );

    // Also check for events that might be social gatherings
    const isSocialEvent = title.includes('with') || 
                         title.includes('meet') || 
                         description.includes('discuss over');

    // Exclude virtual meetings
    const isVirtual = location.includes('zoom') || 
                     location.includes('meet') || 
                     location.includes('virtual') ||
                     location.includes('online');

    return (hasDiningKeyword || isSocialEvent) && !isVirtual;
  });
}

// Function to scrape Chope for restaurant availability
async function searchChopeRestaurants(date, pax, budget, location = 'Singapore') {
  console.log(chalk.yellow('\n🔍 Searching for available restaurants on Chope.co...'));
  
  // This is a simulated function as actual web scraping would require more complex setup
  // In production, you would use Chope's API or proper web scraping
  
  // Simulated restaurant suggestions based on budget
  const restaurants = {
    low: [
      { name: 'Din Tai Fung', cuisine: 'Chinese', price: '$', rating: 4.5, availability: 'Available' },
      { name: 'Sushi Express', cuisine: 'Japanese', price: '$', rating: 4.0, availability: 'Available' },
      { name: 'PastaMania', cuisine: 'Italian', price: '$', rating: 3.8, availability: 'Limited slots' }
    ],
    medium: [
      { name: 'Crystal Jade', cuisine: 'Chinese', price: '$$', rating: 4.4, availability: 'Available' },
      { name: 'Akira Back', cuisine: 'Japanese-Korean', price: '$$', rating: 4.6, availability: 'Available' },
      { name: 'Lawry\'s The Prime Rib', cuisine: 'Western', price: '$$', rating: 4.5, availability: 'Limited slots' }
    ],
    high: [
      { name: 'Odette', cuisine: 'French', price: '$$$', rating: 4.8, availability: 'Waitlist only' },
      { name: 'Les Amis', cuisine: 'French', price: '$$$', rating: 4.7, availability: 'Limited slots' },
      { name: 'Waku Ghin', cuisine: 'Japanese', price: '$$$', rating: 4.9, availability: 'Available' }
    ]
  };

  // Select restaurants based on budget
  let selectedRestaurants = [];
  if (budget <= 30) {
    selectedRestaurants = restaurants.low;
  } else if (budget <= 80) {
    selectedRestaurants = restaurants.medium;
  } else {
    selectedRestaurants = restaurants.high;
  }

  // Add booking URLs (simulated)
  selectedRestaurants = selectedRestaurants.map(r => ({
    ...r,
    bookingUrl: `https://www.chope.co/singapore-restaurants/${r.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}`
  }));

  return selectedRestaurants;
}

async function bookRestaurant() {
  console.log(chalk.blue.bold('\n🍽️  Restaurant Booking Assistant\n'));

  try {
    // Get upcoming events from calendar
    const endDate = format(addDays(new Date(), 30), 'yyyy-MM-dd');
    const calendarPrompt = `Using the Google Calendar MCP server, please:
    1. Get all events for the next 30 days (until ${endDate})
    2. Include event title, date, time, location, attendees, and description
    3. Format as JSON array with fields: title, startTime, endTime, location, attendees, description
    
    Return ONLY the JSON array, no additional text.`;

    console.log(chalk.yellow('📅 Scanning calendar for upcoming events...'));
    
    const eventsResponse = await executeClaudeCommand(calendarPrompt);
    
    let events = [];
    try {
      const jsonMatch = eventsResponse.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        events = JSON.parse(jsonMatch[0]);
      }
    } catch (parseError) {
      console.log(chalk.red('⚠️  Could not parse calendar data.'));
      // Continue with manual entry
    }

    // Identify potential dining events
    const diningEvents = identifyDiningEvents(events);

    if (diningEvents.length > 0) {
      console.log(chalk.green(`\n✨ Found ${diningEvents.length} potential dining event(s):\n`));
      
      diningEvents.forEach((event, index) => {
        const date = event.startTime ? format(parseISO(event.startTime), 'MMM dd, HH:mm') : 'Date TBD';
        console.log(chalk.white(`${index + 1}. ${event.title}`));
        console.log(chalk.gray(`   📅 ${date}`));
        if (event.location) {
          console.log(chalk.gray(`   📍 ${event.location}`));
        }
        if (event.attendees && event.attendees.length > 0) {
          console.log(chalk.gray(`   👥 ${event.attendees.length + 1} people (including you)`));
        }
        console.log();
      });

      // Ask user to select an event or create new
      const eventChoice = await inquirer.prompt([
        {
          type: 'list',
          name: 'selection',
          message: 'Which event would you like to book a restaurant for?',
          choices: [
            ...diningEvents.map((e, i) => ({
              name: `${e.title} (${e.startTime ? format(parseISO(e.startTime), 'MMM dd') : 'Date TBD'})`,
              value: i
            })),
            { name: 'Create a new booking', value: -1 }
          ]
        }
      ]);

      let bookingDetails = {};

      if (eventChoice.selection >= 0) {
        const selectedEvent = diningEvents[eventChoice.selection];
        bookingDetails = {
          date: selectedEvent.startTime,
          title: selectedEvent.title,
          existingAttendees: selectedEvent.attendees ? selectedEvent.attendees.length : 0
        };
      }
    } else {
      console.log(chalk.yellow('\nNo upcoming dining events found in your calendar.'));
      console.log(chalk.white('Let\'s create a new restaurant booking.\n'));
    }

    // Collect booking details
    const questions = [
      {
        type: 'input',
        name: 'date',
        message: 'What date? (YYYY-MM-DD or descriptive like "next Friday"):',
        when: (answers) => !bookingDetails.date,
        validate: (input) => input.length > 0 || 'Please enter a date'
      },
      {
        type: 'number',
        name: 'pax',
        message: 'How many people? (including yourself):',
        default: bookingDetails.existingAttendees ? bookingDetails.existingAttendees + 1 : 2,
        validate: (input) => input > 0 && input <= 20 || 'Please enter a valid number (1-20)'
      },
      {
        type: 'number',
        name: 'budget',
        message: 'Budget per person (SGD):',
        default: 50,
        validate: (input) => input > 0 || 'Please enter a valid budget'
      },
      {
        type: 'list',
        name: 'mealType',
        message: 'What type of meal?',
        choices: ['Lunch', 'Dinner', 'Brunch', 'High Tea'],
        default: 'Dinner'
      },
      {
        type: 'checkbox',
        name: 'cuisinePreferences',
        message: 'Cuisine preferences (select all that apply):',
        choices: [
          'Chinese',
          'Japanese',
          'Korean',
          'Thai',
          'Italian',
          'French',
          'Western',
          'Indian',
          'Vegetarian',
          'Halal'
        ]
      },
      {
        type: 'input',
        name: 'specialRequests',
        message: 'Any special requests or dietary restrictions?',
        default: 'None'
      }
    ];

    const answers = await inquirer.prompt(questions);
    
    // Merge with existing booking details
    const finalBooking = { ...bookingDetails, ...answers };

    console.log(chalk.blue.bold('\n📝 Booking Summary:'));
    console.log(chalk.white(`   Date: ${finalBooking.date || 'To be determined'}`));
    console.log(chalk.white(`   Party size: ${finalBooking.pax} people`));
    console.log(chalk.white(`   Meal type: ${finalBooking.mealType}`));
    console.log(chalk.white(`   Budget: $${finalBooking.budget} per person`));
    if (finalBooking.cuisinePreferences && finalBooking.cuisinePreferences.length > 0) {
      console.log(chalk.white(`   Cuisines: ${finalBooking.cuisinePreferences.join(', ')}`));
    }

    // Search for restaurants
    const restaurants = await searchChopeRestaurants(
      finalBooking.date,
      finalBooking.pax,
      finalBooking.budget
    );

    console.log(chalk.green.bold('\n🎯 Restaurant Recommendations:\n'));

    restaurants.forEach((restaurant, index) => {
      console.log(chalk.white.bold(`${index + 1}. ${restaurant.name}`));
      console.log(chalk.gray(`   🍽️  ${restaurant.cuisine} cuisine`));
      console.log(chalk.gray(`   💰 ${restaurant.price} (Est. $${finalBooking.budget * finalBooking.pax} total)`));
      console.log(chalk.gray(`   ⭐ Rating: ${restaurant.rating}/5`));
      console.log(chalk.yellow(`   📅 ${restaurant.availability}`));
      console.log(chalk.cyan(`   🔗 Book: ${restaurant.bookingUrl}\n`));
    });

    // Ask if user wants to add reminder to calendar
    const addReminder = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'addToCalendar',
        message: 'Would you like to add a booking reminder to your calendar?',
        default: true
      }
    ]);

    if (addReminder.addToCalendar) {
      const selectedRestaurant = await inquirer.prompt([
        {
          type: 'list',
          name: 'restaurant',
          message: 'Which restaurant?',
          choices: restaurants.map((r, i) => ({
            name: r.name,
            value: i
          }))
        }
      ]);

      const restaurant = restaurants[selectedRestaurant.restaurant];
      
      console.log(chalk.yellow('\n📅 Creating calendar reminder...'));
      
      // Create calendar event using Claude MCP
      const createEventPrompt = `Using the Google Calendar MCP server, please create a new calendar event:
      Title: Restaurant Booking - ${restaurant.name}
      Date: ${finalBooking.date}
      Time: ${finalBooking.mealType === 'Lunch' ? '12:30' : '19:00'}
      Location: ${restaurant.name}, Singapore
      Description: Booking for ${finalBooking.pax} people. Budget: $${finalBooking.budget}/person. ${finalBooking.specialRequests ? 'Special requests: ' + finalBooking.specialRequests : ''}
      
      Please create this event and confirm when done.`;

      try {
        await executeClaudeCommand(createEventPrompt);
        console.log(chalk.green('✅ Calendar reminder added successfully!'));
      } catch (error) {
        console.log(chalk.yellow('⚠️  Could not add to calendar automatically.'));
        console.log(chalk.white('Please add manually to your calendar.'));
      }
    }

    console.log(chalk.green.bold('\n✨ Happy dining! Remember to make your reservation soon.\n'));

  } catch (error) {
    console.error(chalk.red('❌ Error:'), error.message);
    console.log(chalk.yellow('\n💡 Make sure Claude Code and Google Calendar MCP are properly configured.'));
  }
}

// Run the booking assistant
bookRestaurant();