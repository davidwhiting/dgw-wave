import logging
from h2o_wave import main, app, Q, ui, on, run_on, data, expando_to_dict
from typing import Optional, List
import sys
import traceback

import frontend
from frontend import add_card, clear_cards, show_error, crash_report

import utils # contains backend

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)

# App name and repo URL for error reporting
app_name = 'My App'

@on('#page1')
async def page1(q: Q):
    await frontend.page1(q)

@on('#page2')
async def page2(q: Q):
    await frontend.page2(q)

@on('#page3')
async def page3(q: Q):
    await frontend.page3(q)

@on('#page4')
@on('page4_reset')
async def page4(q: Q):
    await frontend.page4(q)

@on()
async def page4_step2(q: Q):
    await frontend.page4_step2(q)

@on()
async def page4_step3(q: Q):
    await frontend.page4_step3(q)

@on()
async def reload(q: Q): 
    await frontend.reload(q)

@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """
    try:
        # Initialize the app if not already
        if not q.app.initialized:
            q.app.initialized = True
            logging.info('Initializing app')
            # Add app-level initialization logic here (loading datasets, database connections, etc.)

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
            await frontend.initialize_client(q)

        # Handle page navigation and other events
        await run_on(q)

    except Exception as error:
        await show_error(q, error=str(error))

    await q.page.save()