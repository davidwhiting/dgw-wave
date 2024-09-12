# File descriptions:
# - app.py: logic for the app
# - frontend.py: components of the Wave UI
# - cards.py: card definitions used by frontend
# - utils: backend functions only 
#
# To ensure no circular references:
# - app.py imports frontend.py and utils.py
#   - frontend.py imports cards.py and utils.py
#     - cards.py imports nothing
#     - utils.py imports nothing

from h2o_wave import main, app, Q, ui, on, run_on, data, expando_to_dict
from typing import Optional, List
import logging
import traceback
import sys

import cards
import utils

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)

async def show_error(q: Q, error: str):
    """
    Displays errors.
    """
    logging.error(error)

    # Clear all cards
    clear_cards(q)

    # Format and display the error
    q.page['error'] = crash_report(q)

    await q.page.save()

def crash_report(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
    """
    repo_url = 'https://github.com/your-repo-url'
    issue_url = f'{repo_url}/issues/new?assignees=your-username&labels=bug&template=error-report.md&title=%5BERROR%5D'

    def code_block(content): return '\n'.join(['```', *content, '```'])

    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)

    dump = [
        '### Stack Trace',
        code_block(stack_trace),
    ]

    states = [
        ('q.app', q.app),
        ('q.user', q.user),
        ('q.client', q.client),
        ('q.events', q.events),
        ('q.args', q.args)
    ]
    for name, source in states:
        dump.append(f'### {name}')
        dump.append(code_block([f'{k}: {v}' for k, v in expando_to_dict(source).items()]))

    return ui.form_card(
        box='content',
        items=[
            ui.stats(
                items=[
                    ui.stat(
                        label='',
                        value='Oops!',
                        caption='Something went wrong',
                        icon='Error'
                    )
                ],
            ),
            ui.separator(),
            ui.text_l(content='Apologies for the inconvenience!'),
            ui.buttons(items=[ui.button(name='reload', label='Reload', primary=True)]),
            ui.expander(name='report', label='Error Details', items=[
                ui.text(
                    f'To report this issue, <a href="{issue_url}" target="_blank">please open an issue</a> with the details below:'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )

async def page1(q: Q):
    q.page['sidebar'].value = '#page1'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(3):
        add_card(q, f'info{i}', cards.page1_card1)
    add_card(q, 'article', cards.page1_card4)

async def page2(q: Q):
    q.page['sidebar'].value = '#page2'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'chart1', cards.page2_card1)
    add_card(q, 'chart2', cards.page2_card2)
    add_card(q, 'table', cards.page2_card3)

async def page3(q: Q):
    q.page['sidebar'].value = '#page3'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).

    for i in range(12):
        add_card(q, f'item{i}', cards.page3_card1)

async def page4(q: Q):
    q.page['sidebar'].value = '#page4'
    # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    # Since this page is interactive, we want to update its card
    # instead of recreating it every time, so ignore 'form' card on drop.
    clear_cards(q, ['form'])

    # If first time on this page, create the card.
    add_card(q, 'form', cards.page4_card1)

async def page4_step2(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2'),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox2', label='Textbox 2'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_step3', label='Next', primary=True),
        ])
    ]

async def page4_step3(q: Q):
    # Just update the existing card, do not recreate.
    q.page['form'].items = [
        ui.stepper(name='stepper', items=[
            ui.step(label='Step 1', done=True),
            ui.step(label='Step 2', done=True),
            ui.step(label='Step 3'),
        ]),
        ui.textbox(name='textbox3', label='Textbox 3'),
        ui.buttons(justify='end', items=[
            ui.button(name='page4_reset', label='Finish', primary=True),
        ])
    ]

async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """
    logging.info('Initializing client')

    q.page['meta'] = cards.meta_card
    q.page['sidebar'] = cards.sidebar_card(q)
    q.page['header'] = cards.header_card

    # Mark as initialized at the client (browser tab) level
    q.client.initialized = True
    q.client.cards = set()

    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)

    await q.page.save()

async def reload(q: Q): 
    """
    Reset the client (browser tab).
    This function is called when the user clicks "Reload" on the crash report.
    """
    logging.info('Reloading client')
    q.client.initialized = False
    await initialize_client(q)