Fade light birghtness and color during the day.
Warmer light in the evening.  Dim light at night
and bright light in the morning to ensure you're
awake.

Like redshift / night light / etc for your home.

It uses an `input_select` component for each light
group to control if it should be faded or not.

They look like this:

```
input_select:
  light_mode_livingroom:
    name: Light Mode
    options:
      - "auto"
      - "manual"
```

If the brightness or color is changed it automatically
switches to "manual".  If you turn off your light and
back on, it switches back to "auto".

Variables in the script


 * `GROUPS`
 * `TIME_TABLE`