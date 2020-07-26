*** Settings ***
Library    PuppeteerLibrary
Library    PuppeteerPercy
Library    Dialogs    
Test Teardown    Close Browser


*** Test Cases ***
Capture http page screenshot
    ${HEADLESS}     Get variable value    ${HEADLESS}    ${False}
    &{options} =    create dictionary   headless=${HEADLESS}
    Open browser    http://example.com  options=${options}
    Maximize Browser Window
    Percy Snapshot    HTTP page

Capture https page screenshot
    ${HEADLESS}     Get variable value    ${HEADLESS}    ${False}
    &{options} =    create dictionary   headless=${HEADLESS}
    Open browser    https://www.w3schools.com/  options=${options}
    Maximize Browser Window
    Percy Snapshot    HTTPs page
    