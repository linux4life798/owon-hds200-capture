# HDS200 Series SCPI Protocol Reference

This document provides a reference for the Standard Commands for Programmable Instruments (SCPI) protocol implementation for the HDS200 Series Handheld Oscilloscope.
It's designed for programmers implementing remote control interfaces.

It is a transcription with corrections to https://files.owon.com.cn/software/Application/HDS200_Series_SCPI_Protocol.pdf.

<details>
<summary><b>SCPI Syntax Fundamentals</b></summary>

SCPI commands use a hierarchical tree structure with multiple subsystems. Key syntax elements:

- Commands start with `:` (e.g., `:ACQuire:MODE SAMPle`)
- Keywords are separated by `:`
- Parameters are separated from commands by a space
- Query commands end with `?`
- Command abbreviation: Capital letters represent the short form (e.g., `:ACQ` for `:ACQuire`)
- Case insensitive: `:ACQUIRE`, `:acquire`, and `:Acquire` are equivalent

**Mnemonics Formatting Rules**

1. Words ≤ 4 letters: Use the entire word (e.g., "FREE" for "Free")
2. Words > 4 letters: Use first four letters (e.g., "FREQ" for "Frequency")
3. If 4th letter is a vowel (a,e,i,o,u): Use first three letters (e.g., "POW" for "Power")
4. For phrases: Use first letters of initial words + whole last word (e.g., "IVOLtage" for "Input Voltage")

**Symbol Usage**

- **Space**: Separates command and parameter
- **Colon (`:`)**: Denotes root command (at start) or moves to next level
- **Asterisk (`*`)**: Indicates an IEEE488.2 common command
- **Braces (`{}`)**: Enclose optional parameters, separated by vertical bars
- **Vertical Bar (`|`)**: Separates parameter options
- **Triangle Brackets (`<>`)**: Indicate a parameter placeholder

**Parameter Types**

1. **Discrete**: One of a list of values (e.g., `{CH1|CH2|EXT|EXT/5}`)
2. **Integer**: A whole number in the effective range (NR1 format)
3. **Bool**: `OFF` or `ON`

</details>

<details>
<summary><b>Command Usage Examples</b></summary>

**Basic Identification**
```
*IDN?
```
Response: `XXXX,XXXXXXX,2128009,V2.1.1.5`

**Setting Channel Display and Parameters**
```
:CH1:DISPlay ON
:CH1:COUPling DC
:CH1:PROBe 10X
:CH1:SCALe 1v
```

**Configuring Trigger**
```
:TRIGger:SINGle:SOURce CH1
:TRIGger:SINGle:EDGe:LEVel 25mv
:TRIGger:SINGle:SWEEp NORMal
```

**Reading Waveform Data**
```
:DATa:WAVe:SCReen:HEAD?
:DATa:WAVe:SCReen:CH1?
```

**Setting Up Waveform Generator**
```
:FUNCtion SINE
:FUNCtion:FREQuency 10000
:FUNCtion:AMPLitude 1.5
:FUNCtion:OFFSet 0
```

</details>

## IEEE488.2 Common Commands

| Command | Description |
|---------|-------------|
| `*IDN?` | Returns device identification string as `<Manufacturer>,<model>,<serial number>,X.XX.XX` |
| `*RST` | Seems to reset the device communication. Undocumented. |

## Oscilloscope Commands

### Horizontal Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:HORIzontal:SCALe <value>`<br>`:HORIzontal:SCALe?` | Time base values from 2.0ns to 1000s, options shown bellow | Sets/Queries main timebase scale. |
| `:HORIzontal:OFFset <value>`<br>`:HORIzontal:OFFset?` | Integer: Grid offset<br>Default: 0 | Sets/Queries horizontal offset. |

Time base values:
* `2.0ns`, `5.0ns`, `10.0ns`, `20.0ns`, `50.0ns`, `100ns`, `200ns`, `500ns`
* `1.0us`, `2.0us`, `5.0us`, `10us`, `20us`, `50us`, `100us`, `200us`, `500us`
* `1.0ms`, `2.0ms`, `5.0ms`, `10ms`, `20ms`, `50ms`, `100ms`, `200ms`, `500ms`
* `1.0s`, `2.0s`, `5.0s`, `10s`, `20s`, `50s`, `100s`, `200s`, `500s`, `1000s`

### Acquisition Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:ACQuire:MODe <type>`<br>`:ACQuire:MODe?` | `SAMPle` or `PEAK`<br>Default: `SAMP` | Sets/Queries acquisition mode. |
| `:ACQuire:DEPMem <mdep>`<br>`:ACQuire:DEPMem?` | `4K` or `8K`<br>Default: `4K` | Sets/Queries memory depth. |

### Channel Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:CH<n>:DISPlay <bool>`<br>`:CH<n>:DISPlay?` | n: `1` or `2`<br>bool: `OFF` or `ON`<br>Default: `OFF` | Turns/Queries channel display on/off. |
| `:CH<n>:COUPling <coupling>`<br>`:CH<n>:COUPling?` | n: `1` or `2`<br>coupling: `AC`, `DC`, or `GND`<br>Default: `DC` | Sets/Queries channel coupling mode. |
| `:CH<n>:PROBe <atten>`<br>`:CH<n>:PROBe?` | n: `1` or `2`<br>atten: `1X`, `10X`, `100X`, `1000X`, `10000X` | Sets/Queries probe attenuation ratio. |
| `:CH<n>:SCALe <scale>`<br>`:CH<n>:SCALe?` | n: `1` or `2`<br>scale: shown bellow | Sets/Queries vertical scale in volts, as the device would display, accounting for prob attenuation. |
| `:CH<n>:OFFSet <offset>`<br>`:CH<n>:OFFSet?` | n: `1` or `2`<br>offset: -200 to 200<br>Default: 0 | Sets/Queries vertical offset in volts (units not present). |

Available scales by probe attenuation:
- 1X: `10.0mV`, `20.0mV`, `50.0mV`, `100mV`, `200mV`, `500mV`, `1.00V`, `2.00V`, `5.00V`, `10.0V`
- 10X: `100mV`, `200mV`, `500mV`, `1.00V`, `2.00V`, `5.00V`, `10.0V`, `20.0V`, `50.0V`, `100V`
- 100X: `1.00V`, `2.00V`, `5.00V`, `10.0V`, `20.0V`, `50.0V`, `100V`, `200V`, `500V`, `1.00kV`
- 1000X: `10.0V`, `20.0V`, `50.0V`, `100V`, `200V`, `500V`, `1.00kV`, `2.00kV`, `5.00kV`, `10.0kV`
- 10000X: `100V`, `200V`, `500V`, `1000V`, `2000V`, `5000V`, `10000V`, `20000V`, `50000V`, `100000V`

### Data Commands

**IMPORTANT**: The following commands' response begins with a return data with a 4-byte header indicating the total number of data bytes that follow. This header is in little-endian binary format. For example, if the header bytes are 0x20, 0x4E, 0x00, 0x00, this indicates 20,000 bytes (0x4E20) of data will follow.

| Command | Description |
|---------|-------------|
| `:DATa:WAVe:SCReen:HEAD?` | Returns file header of screen waveform data in JSON format. |
| `:DATa:WAVe:SCReen:CH<x>?` | Returns screen waveform data of specified channel (x: CH1 or CH2)<br>**Note**: Data points are recorded as signed 8-bit values. The reference program seems to average each two points. |

The device displayed scale is the product of the probe and scale, from this head.
For example, when the head query reports a scale of `200mV` and a probe of
`10X`, the device would actually display a scale of `2.00V` per division.

Do note that these data points are not the values directly from the ADC.
If you are looking the exact ADC values (4k or 8k of them), you would need to
save the waveform on the device and download the CSV file using the mass
storage mode. That being said, we can take these simplified screen data points
and convert them to their approximate voltages, using the bellow conversion
formula:

$$
\frac{\text{value} - \text{offset}}{100}
\times 4 \times \text{probe} \times \text{scale}
$$

*The scale and offset values are the ones from the head JSON header.
The probe variable refers to the probe attenuation.*

<details>
<summary>Example:</summary>

1. Query `:DATa:WAVe:SCReen:head?`

    ```json
    {
      //..
      "CHANNEL": [
            {
                "NAME": "CH1",
                "DISPLAY": "ON",
                "COUPLING": "DC",
                "PROBE": "10X",
                "SCALE": "200mV",
                "OFFSET": 50,
                "FREQUENCE": 1000.0
            },
            //...
      ]
    }
    ```

2. Query `:DATa:WAVe:SCReen:ch1?`

    ```
    90 90 90 90 90 90 ...
    ```
3. The first value of `90` would equate to the following voltage:

    $$\frac{90 - 50}{100} \times 4 \times 10 \times 0.2\text{V}
    = \frac{40}{100} \times 4 \times 2\text{V}
    = 3.2\text{V}$$

</details>

<details>
<summary>Example <code>:DATa:WAVe:SCReen:head?</code> query</summary>

```scpi
:DATa:WAVe:SCReen:head?
```

```json
{
    "TIMEBASE": {
        "SCALE": "500us",
        "HOFFSET": 0
    },
    "SAMPLE": {
        "FULLSCREEN": 600,
        "SLOWMOVE": -1,
        "DATALEN": 600,
        "SAMPLERATE": "1MSa/s",
        "TYPE": "SAMPle",
        "DEPMEM": "8K"
    },
    "CHANNEL": [
        {
            "NAME": "CH1",
            "DISPLAY": "ON",
            "COUPLING": "DC",
            "PROBE": "10X",
            "SCALE": "200mV",
            "OFFSET": 50,
            "FREQUENCE": 1000.0
        },
        {
            "NAME": "CH2",
            "DISPLAY": "OFF",
            "COUPLING": "DC",
            "PROBE": "1X",
            "SCALE": "2.00V",
            "OFFSET": -82,
            "FREQUENCE": 0.0
        }
    ],
    "DATATYPE": "SCREEN",
    "RUNSTATUS": "TRIG",
    "IDN": "owon_v1.2",
    "MODEL": "HDS272S_1",
    "Trig": {
        "Mode": "SINGle",
        "Type": "Edge",
        "Items": {
            "Channel": "CH1",
            "Level": "1.52V",
            "Edge": "RISE",
            "Coupling": "DC",
            "Sweep": "AUTO"
        }
    }
}
```

Do note that the individual query commands for scale and offset (seen bellow)
are reported as the device's user facing voltage value, which take into account
the probe attenuation. These do not match the scale and offset from head
(seen above).

```scpi
> :ch1:scale?
2.00V
> :ch1:offset?
2.00
> :ch1:probe?
10X

> :ch2:scale?
2.00V
> :ch2:offset?
-3.28
> :ch2:probe?
1X
```
*The scale, offset, and probe from the same session as the above head query.*
</details>

### Trigger Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:TRIGger:STATus?` | - | Returns current trigger status: `AUTo`, `READy`, `TRIG`, `SCAN`, or `STOP` |
| `:TRIGger:SINGle:SOURce <source>`<br>`:TRIGger:SINGle:SOURce?` | `CH1` or `CH2`<br>Default: `CH1` | Sets/Queries trigger source. |
| `:TRIGger:SINGle:COUPling <coupling>`<br>`:TRIGger:SINGle:COUPling?` | `DC` or `AC`<br>Default: `DC` | Sets/Queries trigger coupling mode. |
| `:TRIGger:SINGle:EDGe <slope>`<br>`:TRIGger:SINGle:EDGe?` | `RISE` or `FALL`<br>Default: `RISE` | Sets/Queries trigger slope. |
| `:TRIGger:SINGle:EDGe:LEVel <level>`<br>`:TRIGger:SINGle:EDGe:LEVel?` | Value with units (uv, mv, v) | Sets/Queries trigger level. |
| `:TRIGger:SINGle:SWEep <mode>`<br>`:TRIGger:SINGle:SWEep?` | `AUTO`, `NORMal`, or `SINGle`<br>Default: `AUTO` | Sets/Queries trigger mode. |

### Measurement Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:MEASurement:DISPlay <bool>`<br>`:MEASurement:DISPlay?` | `OFF` or `ON`<br>Default: `OFF` | Turns/Queries measurement display on/off. |
| `:MEASurement:CH<n>:<items>?` | n: `1` or `2`<br>items: `MAX`, `MIN`, `PKPK`, `VAMP`, `AVERage`, `PERiod`, `FREQuency` | Returns measurement value for specified item |

Measurement item descriptions:
- MAX: Maximum amplitude
- MIN: Minimum amplitude
- PKPK: Peak-to-peak value
- VAMP: Amplitude (Vtop - Vbase)
- AVERage: Average value
- PERiod: Period
- FREQuency: Frequency

## Waveform Generator Commands (Optional)

### Function Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:FUNCtion <waveform>`<br>`:FUNCtion?` | `SINE`, `SQUare`, `RAMP`, `PULSe`, `AmpALT`, `AttALT`, `StairDn`, `StairUD`, `StairUp`, `Besselj`, `Bessely`, `Sinc` | Sets/Queries waveform type. |
| `:FUNCtion:FREQuency <frequency>`<br>`:FUNCtion:FREQuency?` | Floating point (Hz)<br>Note: Not available for DC or noise | Sets/Queries output frequency. |
| `:FUNCtion:PERiod <period>`<br>`:FUNCtion:PERiod?` | Floating point (seconds)<br>Note: Not available for DC or noise | Sets/Queries output period. |
| `:FUNCtion:AMPLitude <amplitude>`<br>`:FUNCtion:AMPLitude?` | Floating point (Vpp)<br>Note: Not available for DC | Sets/Queries amplitude (peak-to-peak). |
| `:FUNCtion:OFFSet <offset>`<br>`:FUNCtion:OFFSet?` | Floating point (V) | Sets/Queries DC offset. |
| `:FUNCtion:HIGHt <high>`<br>`:FUNCtion:HIGHt?` | Floating point (V) | Sets/Queries high level. |
| `:FUNCtion:LOW <low>`<br>`:FUNCtion:LOW?` | Floating point (V) | Sets/Queries low level. |
| `:FUNCtion:SYMMetry <symmetry>`<br>`:FUNCtion:SYMMetry?` | Integer percentage | Sets/Queries ramp waveform symmetry. |
| `:FUNCtion:WIDTh <width>`<br>`:FUNCtion:WIDTh?` | Floating point (seconds) | Sets/Queries pulse width. |
| `:FUNCtion:RISing <time>`<br>`:FUNCtion:RISing?` | Floating point (seconds) | Sets/Queries rising time. |
| `:FUNCtion:FALing <time>`<br>`:FUNCtion:FALing?` | Floating point (seconds) | Sets/Queries falling time. |
| `:FUNCtion:DTYCycle <duty>`<br>`:FUNCtion:DTYCycle?` | Floating point percentage | Sets/Queries pulse duty cycle. |
| `:FUNCtion:LOAD <bool>`<br>`:FUNCtion:LOAD?` | `ON` or `OFF` | Sets/Queries load state. |

Frequency limitations by model:
- HDS242(S)/HDS272(S)/HDS2102(S)/HDS2202(S):
  - Sine: 0.1Hz-25MHz
  - Square: 0.1Hz-5MHz
  - Ramp: 0.1Hz-1MHz
  - Pulse: 0.1Hz-5MHz
  - EXP: 0.1Hz-5MHz

### Channel Control Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:CHANnel <bool>`<br>`:CHANnel?` | `ON`/`OFF` or `1`/`0` | Sets/Queries current channel state. |

## Multimeter Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `:DMM:CONFigure <function>`<br>`:DMM:CONFigure?` | `RESistance`, `DIODe`, `CONTinuity`, or `CAPacitance` | Sets/Queries measurement function. |
| `:DMM:CONFigure:VOLTage <type>`<br>`:DMM:CONFigure:VOLTage?` | `AC` or `DC` | Sets/Queries voltage measurement type. |
| `:DMM:CONFigure:CURRent <type>`<br>`:DMM:CONFigure:CURRent?` | `AC` or `DC` | Sets/Queries current measurement type. |
| `:DMM:REL <state>`<br>`:DMM:REL?` | `ON` or `OFF` | Sets/Queries relative measurement mode. |
| `:DMM:RANGE <position>`<br>`:DMM:RANGE?` | `ON`: Switch to next tap position<br>`mV`: Switch to mV tap position<br>`V`: Switch to V tap position | Sets/Queries range position. |
| `:DMM:AUTO ON`<br>`:DMM:AUTO?` | - | Enables/Queries auto range state. |
| `:DMM:MEAS?` | - | Returns measured value displayed by multimeter |

## Notes and Potential Issues

1. **Documentation Inconsistency**: The command `:TRIGger:SINGle:EDGe` appears in two forms in the documentation - one with a single colon after SINGle and another with two colons (`:TRIGger:SINGle::EDGe`). The correct form is likely the first one. It also shows in the example `:TRIGger:SINGle:SLOPe` instead of `:TRIGger:SINGle:EDGe`.

2. **Data Format Issue**: The documentation mentions for `:DATa:WAVe:SCReen:CH<x>?` that "The data point is recorded as 8-bit, a point uses two bytes, little-endian byte order." This could be confusing - if it's 8-bit, it should be one byte. This needs to be verified.

3. **Parameter Range Completeness**: Some commands have limited documentation about valid parameter ranges. Developers should test the boundaries for parameters like frequency, amplitude, etc.

4. **Character Encoding**: The documentation doesn't specify character encoding for string responses. ASCII is implied, but UTF-8 compatibility should be verified.

5. **Device Hanging Issue**: The HDS272S itself hangs if you try to enable/disable a measurement like `:MEASurement:ch1 min`.
