#!/usr/bin/env node

import chalk from 'chalk';
import { spawn } from 'child_process';
import { format, parseISO } from 'date-fns';

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

// Helper to calculate travel time estimates
function estimateTravelTime(location1, location2) {
  // Simple estimation based on location keywords
  const isRemote = (loc) => 
    !loc || loc.toLowerCase().includes('zoom') || 
    loc.toLowerCase().includes('meet') || 
    loc.toLowerCase().includes('teams') ||
    loc.toLowerCase().includes('virtual') ||
    loc.toLowerCase().includes('online');

  if (isRemote(location1) || isRemote(location2)) {
    return 0; // No travel time for virtual meetings
  }

  // Default travel time estimate (in minutes)
  if (location1 && location2 && location1 !== location2) {
    return 30; // Default 30 minutes travel between different locations
  }
  
  return 0;
}

async function getMorningBriefing() {
  console.log(chalk.blue.bold('\n☀️  Good Morning! Getting your daily briefing...\n'));

  try {
    // Use Claude with MCP to get calendar events
    const calendarPrompt = `Using the Google Calendar MCP server, please:
    1. Get all events for today
    2. List them in chronological order
    3. Include event title, time, location, and attendees
    4. Format as JSON array with fields: title, startTime, endTime, location, attendees, description
    
    Return ONLY the JSON array, no additional text.`;

    console.log(chalk.yellow('📅 Fetching today\'s calendar events...'));
    
    const eventsResponse = await executeClaudeCommand(calendarPrompt);
    
    let events = [];
    try {
      // Parse the JSON response from Claude
      const jsonMatch = eventsResponse.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        events = JSON.parse(jsonMatch[0]);
      }
    } catch (parseError) {
      console.log(chalk.red('⚠️  Could not parse calendar data. Showing raw response:'));
      console.log(eventsResponse);
      return;
    }

    // Display the daily schedule
    console.log(chalk.green.bold('\n📋 Today\'s Schedule:\n'));

    if (events.length === 0) {
      console.log(chalk.gray('   No events scheduled for today. Enjoy your free day!'));
    } else {
      let previousLocation = null;
      let totalTravelTime = 0;

      events.forEach((event, index) => {
        const startTime = event.startTime ? format(parseISO(event.startTime), 'HH:mm') : 'All day';
        const endTime = event.endTime ? format(parseISO(event.endTime), 'HH:mm') : '';
        
        // Calculate travel time from previous event
        if (previousLocation && event.location) {
          const travelTime = estimateTravelTime(previousLocation, event.location);
          if (travelTime > 0) {
            console.log(chalk.cyan(`   🚗 Travel time: ~${travelTime} minutes`));
            totalTravelTime += travelTime;
          }
        }

        // Event display
        console.log(chalk.white.bold(`\n   ${startTime}${endTime ? '-' + endTime : ''}: ${event.title}`));
        
        if (event.location) {
          const isVirtual = event.location.toLowerCase().includes('zoom') || 
                           event.location.toLowerCase().includes('meet') ||
                           event.location.toLowerCase().includes('virtual');
          const icon = isVirtual ? '💻' : '📍';
          console.log(chalk.gray(`   ${icon} ${event.location}`));
        }
        
        if (event.attendees && event.attendees.length > 0) {
          console.log(chalk.gray(`   👥 ${event.attendees.join(', ')}`));
        }
        
        if (event.description) {
          const shortDesc = event.description.substring(0, 100);
          console.log(chalk.gray(`   📝 ${shortDesc}${event.description.length > 100 ? '...' : ''}`));
        }

        // Highlight important meetings
        const isImportant = event.title.toLowerCase().includes('important') ||
                          event.title.toLowerCase().includes('urgent') ||
                          event.title.toLowerCase().includes('review') ||
                          event.title.toLowerCase().includes('presentation') ||
                          (event.attendees && event.attendees.length > 5);
        
        if (isImportant) {
          console.log(chalk.red.bold('   ⚠️  HIGH PRIORITY'));
        }

        previousLocation = event.location;
      });

      // Daily summary
      console.log(chalk.blue.bold('\n📊 Daily Summary:'));
      console.log(chalk.white(`   • Total events: ${events.length}`));
      
      if (totalTravelTime > 0) {
        const hours = Math.floor(totalTravelTime / 60);
        const minutes = totalTravelTime % 60;
        console.log(chalk.white(`   • Estimated travel time: ${hours > 0 ? hours + 'h ' : ''}${minutes}min`));
      }

      // Count virtual vs in-person meetings
      const virtualMeetings = events.filter(e => 
        e.location && (e.location.toLowerCase().includes('zoom') || 
                      e.location.toLowerCase().includes('meet') ||
                      e.location.toLowerCase().includes('virtual'))
      ).length;
      
      const inPersonMeetings = events.length - virtualMeetings;
      
      if (virtualMeetings > 0) {
        console.log(chalk.white(`   • Virtual meetings: ${virtualMeetings}`));
      }
      if (inPersonMeetings > 0) {
        console.log(chalk.white(`   • In-person meetings: ${inPersonMeetings}`));
      }
    }

    // Time-based recommendations
    const hour = new Date().getHours();
    console.log(chalk.yellow.bold('\n💡 Recommendations:'));
    
    if (hour < 9) {
      console.log(chalk.white('   • Start with your most important task while your energy is high'));
    } else if (hour < 12) {
      console.log(chalk.white('   • Good time for focused work and important meetings'));
    } else if (hour < 14) {
      console.log(chalk.white('   • Consider a lunch break to recharge'));
    } else if (hour < 17) {
      console.log(chalk.white('   • Afternoon is great for collaborative work'));
    } else {
      console.log(chalk.white('   • Wrap up tasks and plan for tomorrow'));
    }

    console.log(chalk.green.bold('\n✨ Have a productive day!\n'));

  } catch (error) {
    console.error(chalk.red('❌ Error fetching calendar data:'), error.message);
    console.log(chalk.yellow('\n💡 Make sure:'));
    console.log('   1. Claude Code is running');
    console.log('   2. Google Calendar MCP server is configured');
    console.log('   3. You have valid OAuth credentials in .claude/credentials/');
    console.log('\nRun "claude mcp list" to check your MCP servers.');
  }
}

// Run the morning briefing
getMorningBriefing();