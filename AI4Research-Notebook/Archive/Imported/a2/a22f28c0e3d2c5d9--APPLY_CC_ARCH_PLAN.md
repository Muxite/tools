# Apply the CC and Architecture plan to the live workbook

The plan only changes the CC rows (1.x) and Architecture rows (8.x). Every other row stays as other people left it. Each step below is one action in Excel, so nobody else's edit can land in the middle of one.

## 1. Build the patched copy (local, about one minute)

1. In the live workbook: File, Save a copy (or Download a copy). Save it in Downloads.
2. Run:
   `python C:\Users\m50066326\huawei\AI4Research_private_planning\apply_cc_arch_plan.py "C:\Users\m50066326\Downloads\<copy>.xlsx"`
3. It writes `<copy> - PATCHED.xlsx` and prints three facts:
   - how many rows to insert in each block (CC and Architecture),
   - where each block sits in the patched copy,
   - the Timeline range.
4. Open the PATCHED copy and look at the Timeline tab. The bars, milestones and grouping should look right before you touch the live file.

Rebuild the copy right before step 2. If someone adds or removes rows in the live workbook after your download, download again and rerun the script.

## 2. Apply to the live workbook (eight single actions, about two minutes)

Open the live workbook and the PATCHED copy side by side.

**Main Table**
1. Select whole rows inside the live CC block, starting at the row just below `1.0`. Select as many rows as the script said to insert for CC, then right-click and choose Insert. The new blank rows sit inside the block.
2. Do the same inside the Architecture block, starting at the row just below `8.0`.
3. In the PATCHED copy, select the CC block range the script printed (columns A to P) and copy it. In the live file, click column A of the `1.0` row and paste.
4. Do the same for the Architecture block, pasting at column A of the live `8.0` row.

**Timeline**

5. On the Timeline tab, insert the same number of whole rows at the same place for CC. The Timeline row equals the Main Table row plus 4.
6. Do the same for Architecture.
7. In the PATCHED copy's Timeline, select the rows that match the CC block. Add 4 to each Main Table row number, for example A9:IP77 when the CC block is A5:P73. Copy them and paste at column A of the live Timeline row that shows `1.0`.
8. Do the same for the Architecture block, pasting at the live Timeline row that shows `8.0`.

## 3. Check

- In the live Timeline, every CC and Architecture row shows its name and its bar. No row shows another row's name.
- The `1.0` and `8.0` rows show dates, not numbers such as 46308.
- Other components' rows are unchanged.

If anything looks wrong, use Undo straight away. Each step is a single undo.

## Notes

- Formulas are copied cell to cell from the PATCHED copy, so Excel adjusts them to where they are pasted. A small row shift elsewhere in the sheet does not break them.
- The script keeps the live status, work details and any field the handoff marks "keep". Any live CC or Architecture row the handoff does not mention is kept at the end of its block and reported as `NOTE: keeping unlisted live row`.
- Dependency cells in other components (RSI 3.1.3 and 3.2.1) were already updated by hand. The script does not touch other components.
