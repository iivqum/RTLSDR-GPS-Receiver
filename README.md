RTLSDR GPS receiver project.

I use custom hardware to make it work. First is the helical RHCP antenna.

<p align="center"><img width="338" height="381" alt="antenna" src="https://github.com/user-attachments/assets/47dd0ebc-549d-44a5-b7f6-b796390a3fec" /></p>

Second is a custom GPS LNA, which includes a filter and a GPS SAW filter I got from AliExpress. There's a second LNA closer to the SDR. Gain of each is
around 23 dB so there are 3 filter stages in the chain and 3 gain stages (including the SDR). I run the SDR with the gain maxed out at 50 dB, resulting
in 96 dB of total gain.

<p align="center"><img width="375" height="500" alt="frontend" src="https://github.com/user-attachments/assets/c6784f3a-d335-489c-8375-130e7d530e54" /></p>

Here's an example acquisition of SV11

<p align="center"><img width="434" height="359" alt="aq" src="https://github.com/user-attachments/assets/032471bd-c70c-4581-b82a-64d6bbdecd04" /></p>
