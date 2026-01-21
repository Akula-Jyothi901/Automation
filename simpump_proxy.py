from socket import *
import sys
import time
import threading
import requests
from threading import Lock
import traceback
from cfrfuelbdd.fuel_logging import logger

PUMP_DELAY_VALUE = 1

##########################################################
##  SimPumpsProxy automates the SimPumps application
##  References : WIT #586015
##               Design document SWAT_Integration_With_SimPumps.doc

class CSimPumpsProxy(object):

    ##################################################
    ##  Constant definitions - not really constant since
    ##                         python does not support them

    TIER_CASH   = 0
    TIER_CREDIT     = 1

    TRUE        = 1
    FALSE       = 0

    CODE_SUCCESS                     = 3000
    CODE_INVALID_PARAMETER_COUNT     = 3001
    CODE_INVALID_PARAMETER           = 3002
    CODE_INVALID_PARAMETER_FORMAT    = 3003
    CODE_INVALID_FUNC_CALL           = 3004
    CODE_DEPRICATED_FUNC             = 3005
    CODE_INTERNAL_FAILURE            = 3006
    CODE_INVALID_COMMAND             = 3007
    CODE_INVALID_VERSION             = 3008
    CODE_PROXY_ERROR                 = 9999

    CHAR_FS                          = '\x1c'



    #  Static data

    version = '1.0.0'
    DEFAULT_IP='192.168.6.100'
    DEFAULT_PORT=2000
    CmdSetScriptFile        = ' | 1 | '
    CmdSetScriptToExecute       = ' | 2 | '
    CmdSetFuelQuantityGallons   = ' | 3 | '
    CmdSetFuelQuantityCents     = ' | 4 | '
    CmdSetFuelGrade         = ' | 5 | '
    CmdSetOverrun           = ' | 6 | ' # used to set overrun strictly to defaultoverrunamount in simpumps
    CmdSetFlowRate          = ' | 7 | '
    CmdSetDelayedAuthorization  = ' | 8 | '
    CmdStartScript          = ' | 9 | '
    CmdStopScript           = ' | 10 | '
    CmdIsScriptRunning      = ' | 11 | '
    CmdSetTier              = ' | 12 | '
    CmdSetLimitDisable      = ' | 15 | '
    CmdSetOverrunAmount     = ' | 17 | ' # can set overrun to specific amount
    CmdSwipeCard            = ' | 20 | '
    CmdScanBarcode          = ' | 21 | '
    CmdScanRFID             = ' | 22 | '
    CmdInsertCard           = ' | 23 | '
    CmdRemoveCard           = ' | 24 | '
    CmdTapCard              = ' | 25 | '
    CmdEnterNumeric         = ' | 30 | '
    CmdPressButton          = ' | 40 | '
    CmdSetHandleState       = ' | 41 | '
    CmdSetFuelingState      = ' | 42 | '
    CmdPressSoftKey         = ' | 43 | '
    CmdGetKeypadEncryptionStatus   = ' | 44 | '
    
    CmdGetCurrentDisplay        = ' | 51 | '
    CmdGetCurrentMoneyDisplay   = ' | 52 | '
    CmdGetCurrentGallonsDisplay = ' | 53 | '
    CmdGetCurrentReceipt        = ' | 54 | '
    CmdGetCurrentPPUDisplay     = ' | 55 | '
    CmdSetPumpState             = ' | 56 |'
    CmdSetICRState              = ' | 57 |'
    CmdResetLastBeepDuration    = ' | 60 | '
    CmdGetLastBeepDuration      = ' | 61 | '
    CmdResetICRCommandHistory   = ' | 62 | '
    CmdGetNextICRCommand        = ' | 63 | '

    CmdGetKeypadStatus          = ' | 64 | '
    CmdSetPrinterState          = ' | 65 | '
    CmdGetMSRStatus             = ' | 66 | '
    CmdGetBCSStatus             = ' | 67 | '
    CmdPumpDisconnect           = ' | 68 | '
    CmdGetPromptWidth           = ' | 69 | '
    CmdGetCurrentDisplayImage   = ' | 70 | '
    CmdCloseSimpumps            = ' | 99 | '
    CmdResetParameters          = ' | 100 | '

    def __init__(self, hostaddress, port):
        self.code = '0'
        self.Message = 'Not Valid'
        self._lock = Lock()
        self.host_address = hostaddress
        if not self._connect_to_host(hostaddress, port):
            assert False, ("*****\n***** ERROR - Cannot connect to SimPumps at " + hostaddress + ":" + str(port) + "\n*****\n")

    def set_cards_file(self, card_file_path):
        self.simpumps_cards.set_cards_file(card_file_path)

    def set_config_file_path(self, config_file_path):
        self._simpumps_chip_prompts.set_config_file_path(config_file_path)

    def _connect_to_host(self, host, port):
        bRetVal = False
        for retry in range(1,20):
            #print("Trying to connect to simpumps retry=%d host=%s port=%d" % (retry, self.host, self.port) )
            self.spSocket = socket(AF_INET,SOCK_STREAM)
            try:
                self.spSocket.connect((host, port))
                bRetVal = True
                self.code = '0'
                self.Message = 'Connected'
                break
            except Exception as e:
                time.sleep(1)
#                print("Simpumps connect fail, wait 1s and retry, err=%s" % str(e))
                self.code = self.CODE_PROXY_ERROR
                self.Message = traceback.format_exc()
        return bRetVal

    def disconnect_from_host(self):
        self.spSocket.close()
  
    
    def set_script_file(self, scriptFile):
        cmd = self.version + self.CmdSetScriptFile + scriptFile
        return self._process_cmd(cmd)

    def set_script_to_execute(self, pump, scriptName):
        cmd = self.version + self.CmdSetScriptToExecute + str(pump) + '|' + scriptName
        return self._process_cmd(cmd)
		
    def get_keypad_encryption_status(self, pump):
        retVal = False
        cmd = self.version + self.CmdGetKeypadEncryptionStatus + str(pump)
        if(self._process_cmd(cmd) == True):
            if(self.Message[:4] == 'True'):
                retVal = True
        return retVal
        
    def set_fuel_quantity_gallons(self, pump, gallons):
        cmd = self.version + self.CmdSetFuelQuantityGallons + str(pump) + '|' + str(gallons)
        return self._process_cmd(cmd)

    def set_disable_fuel_limit(self, pump):
        cmd = self.version + self.CmdSetLimitDisable + str(pump)
        return self._process_cmd(cmd)

    def set_fuel_money(self, pump, money):
        cmd = self.version + self.CmdSetFuelQuantityCents + str(pump) + '|' + str(money)
        return self._process_cmd(cmd)

    def select_grade(self, pump, grade):
        cmd = self.version + self.CmdSetFuelGrade + str(pump) + '|' + str(grade)
        return self._process_cmd(cmd)

    def set_overrun_amount(self, pump, money):
        # possibly would want to screen for negative numbers, Simpumps doesn't do this internally
        if money < 0:
            money = 0
        cmd = self.version + self.CmdSetOverrunAmount + str(pump) + '|' + str(money)
        return self._process_cmd(cmd)

    def set_flow_rate(self, pump, rate):
        cmd = self.version + self.CmdSetFlowRate + str(pump) + '|' + str(rate)
        return self._process_cmd(cmd)

    def set_delayed_authorization(self, pump, auth):
        cmd = self.version + self.CmdSetDelayedAuthorization + str(pump) + '|' + str(auth)
        return self._process_cmd(cmd)

    def start_script(self, pump):
        cmd = self.version + self.CmdStartScript + str(pump)
        return self._process_cmd(cmd)

    def stop_script(self, pump):
        cmd = self.version + self.CmdStopScript + str(pump)
        return self._process_cmd(cmd)

    def is_script_running(self, pump):
        retVal = False

        cmd = self.version + self.CmdIsScriptRunning + str(pump)
        if(self._process_cmd(cmd) == True):
            if(self.Message[0:4] == 'True'):
                retVal = True
        return retVal

    def set_tier(self, pump, tier):
        cmd = self.version + self.CmdSetTier + str(pump) + '|' + str(tier)
        return self._process_cmd(cmd)

    def swipe_card(self, pump, track_data):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdSwipeCard + str(pump) + '|' + str(track_data)
        return self._process_cmd(cmd)

    def scan_barcode(self, pump, barcode):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdScanBarcode + str(pump) + '|' + str(barcode)
        return self._process_cmd(cmd)

    def scan_rfid(self, pump, rfid):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdScanRFID + str(pump) + '|' + str(rfid)
        return self._process_cmd(cmd)

    def insert_card_using_name(self, pump, card_name):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdInsertCard + str(pump) + '|' + str(card_name)
        return self._process_cmd(cmd)
        
    def insert_card(self, pump, card_attributes_string):
        time.sleep(PUMP_DELAY_VALUE)
        card_name = self.simpumps_cards.find_card_name(card_attributes_string)
        if (card_name != None):
              cmd = self.version + self.CmdInsertCard + str(pump) + '|' + str(card_name)
              return self._process_cmd(cmd)
        else:
            return False

    def remove_card(self, pump):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdRemoveCard + str(pump)
        return self._process_cmd(cmd)

    def tap_card_using_name(self, pump, card_name):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdTapCard + str(pump) + '|' + str(card_name)
        return self._process_cmd(cmd)

    def enter_key_sequence(self, pump, sequence):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdEnterNumeric + str(pump) + '|' + str(sequence)
        return self._process_cmd(cmd)

    def press_button(self, pump, button):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdPressButton + str(pump) + '|' + str(button)
        return self._process_cmd(cmd)

    def press_softkey(self, pump, row, column):
        time.sleep(PUMP_DELAY_VALUE)
        cmd = self.version + self.CmdPressSoftKey + str(pump) + '|' + str(row) + '|' + str(column) 
        return self._process_cmd(cmd)
    
    def lift_nozzle(self, pump):
        cmd = self.version + self.CmdSetHandleState + str(pump) + '|' + str(1)
        return self._process_cmd(cmd)
        
    def return_nozzle(self, pump):
        cmd = self.version + self.CmdSetHandleState + str(pump) + '|' + str(0)
        return self._process_cmd(cmd)

    def start_fueling(self, pump):
        cmd = self.version + self.CmdSetFuelingState + str(pump) + '|' + str(1)
        return self._process_cmd(cmd)
        
    def stop_fueling(self, pump):
        cmd = self.version + self.CmdSetFuelingState + str(pump) + '|' + str(0)
        return self._process_cmd(cmd)

    def get_last_result(self):
        return self.code, self.Message

    def get_current_display(self, pump):
        cmd = self.version + self.CmdGetCurrentDisplay + str(pump)
        return self._process_display_cmd(cmd)

    def get_current_display_exact(self, pump):
        cmd = self.version + self.CmdGetCurrentDisplay + str(pump)
        return self._process_display_cmd_exact(cmd)
    
    def get_current_display_image(self, pump):
        cmd = self.version + self.CmdGetCurrentDisplayImage + str(pump)
        return self._process_display_cmd(cmd)

    def get_current_money_display(self, pump):
        cmd = self.version + self.CmdGetCurrentMoneyDisplay + str(pump)
        return self._process_display_cmd(cmd)

    def get_current_gallons_display(self, pump):
        cmd = self.version + self.CmdGetCurrentGallonsDisplay + str(pump)
        return self._process_display_cmd(cmd)

    def get_current_ppu_display(self, pump, hose, tier):
        cmd = self.version + self.CmdGetCurrentPPUDisplay + str(pump) + '|' + str(hose) + '|' + str(tier)
        return self._process_display_cmd(cmd)

    def get_current_receipt(self, pump):
        cmd = self.version + self.CmdGetCurrentReceipt + str(pump)
        return self._process_display_cmd(cmd)

    def reset_last_beep_duration(self, pump):
        cmd = self.version + self.CmdResetLastBeepDuration + str(pump)
        return self._process_cmd(cmd)

    def get_last_beep_duration(self, pump):
        cmd = self.version + self.CmdGetLastBeepDuration + str(pump)
        return self._process_display_cmd(cmd)

    def get_keypad_status(self, pump):
        cmd = self.version + self.CmdGetKeypadStatus + str(pump)
        return self._process_display_cmd(cmd)

    def get_BCS_status(self,pump):
        cmd = self.version + self.CmdGetBCSStatus + str(pump)
        return self._process_display_cmd(cmd)

    def get_MSR_status(self,pump):
        cmd = self.version + self.CmdGetMSRStatus + str(pump)
        return self._process_display_cmd(cmd)

    def get_emvinitialization(self):
        '''
            Gets the EMVInitialization json file
        '''
        return requests.get(url = 'http://' + self.host_address + ':8191/config/emvinitialization')
    
    def send_simpumps_card_config(self, configFile):
        logger.debug("Sending card config to simpumps, %s" % configFile)
        serverAddress = self.host_address
        restUrl = 'http://%s:8191' % serverAddress
        fileContent = ""
        with open(configFile,'r') as file:
            fileContent = file.read()
        r = requests.put(
            url = (restUrl + "/config/card"),
            json = fileContent)

    def get_softkey_labels(self, pump):
        '''
            Get currently displayed softkey labels (for dispensers that support separate softkey labels)
        '''
        return requests.get(url = 'http://' + self.host_address + ':8191/pump/' + str(pump) + '/softkeylabel')
    
    def get_chipcardReader_status(self,pump):
        '''
            Gets the status of the chipcard reader (either enabled or disabled)
        '''
        return requests.get(url = 'http://' + self.host_address + ':8191/command/' + str(pump) + '/ChipReaderStatus')
        
    def get_contactless_chipcardReader_status(self,pump):
        '''
            Gets the status of the contactless chipcard reader (either enabled or disabled)
        '''
        return requests.get(url = 'http://' + self.host_address + ':8191/command/' + str(pump) + '/ContactlessChipReaderStatus')
        
    def reset_parameters(self, pump):
        cmd = self.version + self.CmdResetParameters + str(pump)
        return self._process_cmd(cmd)

    def reset_icr_command_history(self, pump):
        cmd = self.version + self.CmdResetICRCommandHistory + str(pump)
        return self._process_cmd(cmd)

    def get_next_icr_command(self, pump):
        cmd = self.version + self.CmdGetNextICRCommand + str(pump)
        return self._process_display_cmd(cmd)
        
    def set_printer_clear(self, pump):
        cmd = self.version + self.CmdSetPrinterState + str(pump) + '|' + 'Clear' + '|' + 'True'
        return self._process_display_cmd(cmd)
        
    def set_printer_error(self, pump, state):
        cmd = self.version + self.CmdSetPrinterState + str(pump) + '|' + 'Error' + '|' + str(state)
        return self._process_display_cmd(cmd)
        
    def set_printer_paper_low(self, pump, state):
        cmd = self.version + self.CmdSetPrinterState + str(pump) + '|' + 'PaperLow' + '|'+ str(state)
        return self._process_display_cmd(cmd)
        
    def set_printer_paper_out(self, pump, state):
        cmd = self.version + self.CmdSetPrinterState + str(pump) + '|' + 'PaperOut' + '|' + str(state)
        return self._process_display_cmd(cmd)
        
    def set_printer_power(self, pump, state):
        cmd = self.version + self.CmdSetPrinterState + str(pump) + '|' + 'Power' + '|' + str(state)
        return self._process_display_cmd(cmd)
    
    def set_printer_paper_jam(self, pump, state):
        cmd = self.version + self.CmdSetPrinterState + str(pump) + '|' + 'PaperJam' + '|' + str(state)
        return self._process_display_cmd(cmd)
    
    def get_prompt_width(self, pump):
        cmd = self.version + self.CmdGetPromptWidth + str(pump)
        return self._process_display_cmd(cmd)
    
    def set_expected_manual_response(self, void):
        # Used for manual teseting
        pass
        
    def display_user_message(self, void):
        # Used for manual teseting
        pass

    def activate_icr(self, icr):
        cmd = self.version + self.CmdSetICRState + str(icr) + '|' + str(1)
        return self._process_cmd(cmd)

    def activate_pump(self, pump):
        cmd = self.version + self.CmdSetPumpState + str(pump) + '|' + str(1)
        return self._process_cmd(cmd)

    def deactivate_icr(self, icr):
        cmd = self.version + self.CmdSetICRState + str(icr) + '|' + 'False'
        return self._process_cmd(cmd)

    def deactivate_pump(self, pump):
        cmd = self.version + self.CmdSetPumpState + str(pump) + '|' + 'False'
        return self._process_cmd(cmd)
        
    def match_prompt_on_display(self, pump, expected_prompt, match_exactly, timeout, polling_sleep=1):
        """Retrieve the prompt text on ICR.

        :param int pump: Pump number
        :param str expected_prompt: Expected prompt text
        :param bool match_exactly: Match excatly if True, otherwise use contains
        :param int timeout: timeout in seconds
        :param polling_sleep: Amount of time to sleep between polling checks
        :return: True if we found a match within the timeout, otherwise False
        :rtype: str
        """

        currtimer = time.time()
        while (time.time() - currtimer < timeout):
            # get the current prompt
            message = self.get_current_display(pump)

            if match_exactly is False:
                if expected_prompt in message:
                    return True
            else:
                if message == expected_prompt:
                    return True

            time.sleep(polling_sleep)

        return False
        
    def get_prices(self, pump):
        hose_tier_prices = []
        for hose in range(0, 6):
            for tier in range(0, 2):
                cmd = self.version + self.CmdGetCurrentPPUDisplay + str(pump) + '|' + str(hose) + '|' + str(tier)
                self._process_display_cmd(cmd)
                current_price = self._process_display_return(True)
                price = dict()
                price["Hose"] = hose + 1  # since the hose numbers on simpump starts at 0.
                price["Tier"] = tier
                price["Price"] = int(current_price) / 1000  # prices are in 3 decimal precision
                hose_tier_prices.append(price)

        return hose_tier_prices

    def get_chip_prompt_text(self, pump, prompt_name, retry):
        """Get EMV prompt text for given prompt name and pump.

        :param int pump: Pump number
        :param string prompt_name: Name of the prompt
        :param bool retry: Is the prompt a retry prompt
        :return: prompt text for a given pump and prompt name
        :rtype: string
        """

        icr_type_string = self.get_icr_device_type(pump)
        return self._simpumps_chip_prompts.get_chip_prompt(prompt_name, retry, icr_type_string)
    ##################################################
    ##  Helper functions

    def _parse_return(self, data):
        # ignore characters that would cause the decode to fail
        # and split the string
        self.code, self.Message = data.decode("utf-8", "ignore").split('|')
        if(self.code == '3000'):
            return True
        else:
            logger.error(f'Simpumps Error: {self.code} - {self.Message}')
            return False

    def _process_display_return(self, strip_whitespace_flag):
        # Expected format "<message><FS><encoding>" or "<message>" (encoding is expected to be cp1252)
        if(self.code == '3000'):
            message = u''
            components = self.Message.rstrip('\x00').split(self.CHAR_FS)
            if len(components) > 0:
                encoding = components[1].lower() if len(components) > 1 else 'cp1252'
                try:
                    message = components[0]
                except LookupError:
                    message = components[0]

            if(strip_whitespace_flag == True):
                return message.strip()
            return message

    def _process_cmd(self, cmd):
        with self._lock:
            try:
                buff = 4096
                # logger.debug(f'Simpumps >> {cmd}')
                self.spSocket.send(cmd.encode())
                retData = self.spSocket.recv(buff)
                response = retData.decode("utf-8", "ignore").rstrip('\x00')
                # logger.debug(f'Simpumps << {response}')
                return self._parse_return(retData)
            except:
                self.code = self.CODE_PROXY_ERROR
                self.Message = traceback.format_exc()
                logger.debug(f'Exception: {self.code}-{self.Message}')
                return False
                
    def _process_cmd_async(self, cmd):
        with self._lock:
            try:
                #logger.debug(f'Simpumps [async] >> {cmd}')
                self.spSocket.send(cmd.encode())
                return True
            except:
                self.code = self.CODE_PROXY_ERROR
                self.Message = traceback.format_exc()
                logger.debug(f'Exception: {self.code}-{self.Message}')
                return False
                
    def _process_display_cmd(self, cmd):
        self._process_cmd(cmd)
        return self._process_display_return(True)

    def _process_display_cmd_exact(self, cmd):
        self._process_cmd(cmd)
        return self._process_display_return(False)

    def close(self):
        pass
        #cmd = self.version + self.CmdCloseSimpumps
        #return self._process_cmd_async(cmd)
    
    def disconnect_pump(self, pump):
        cmd = self.version + self.CmdPumpDisconnect + str(pump) + '|' + str(1)
        return self._process_cmd(cmd)

    def reconnect_pump(self, pump):
        cmd = self.version + self.CmdPumpDisconnect + str(pump) + '|' + str(0)
        return self._process_cmd(cmd)