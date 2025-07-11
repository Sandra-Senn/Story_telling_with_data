import pandas as pd
import numpy as np
import plotly.graph_objects as go

import re
from typing import Dict




def get_death_year(group):
    death_year = group.loc[~group['überlebt'], 'year']
    return death_year.min() if not death_year.empty else 0



def seen_mit_sterbejahr(df_merged: pd.DataFrame, fisch_namen, szenarien=None) -> pd.DataFrame:
    """
    Gibt für jede Fischart in fisch_namen alle Seen aus, in denen sie vorkommt, und für jedes Szenario das Jahr, 
    in dem der Fisch stirbt.

    Parameters:
        df_merged (pd.DataFrame): Gesamtdaten.
        fisch_namen (list): Liste von Fisch-Namen.
        szenarien (list): Liste der Szenarien (z.B. ['RCP26', 'RCP45', 'RCP85'])

    Returns:
        pd.DataFrame: DataFrame mit Fischname, See und den Sterbejahren pro Szenario.
    """
    if szenarien is None:
        szenarien = ['RCP26', 'RCP45', 'RCP85']
    if isinstance(fisch_namen, str):  # Falls nur ein Name als String übergeben wird
        fisch_namen = [fisch_namen]
    
    results = []
    for fisch_name in fisch_namen:
        # Filter für den angegebenen Fisch (nur EIN Name!)
        df_fisch = df_merged[df_merged['Fisch'] == fisch_name]

        # Gruppieren nach lake und scenario, frühestes Sterbejahr mit get_death_year ermitteln
        df_sterbejahr = (
            df_fisch.groupby(['lake', 'scenario']).apply(get_death_year).unstack(fill_value=0)
        )

        # Alle Seen, in denen der Fisch vorkommt
        alle_seen = df_fisch['lake'].unique()

        # DataFrame erstellen mit allen Seen
        result = pd.DataFrame({'Fisch': fisch_name, 'lake': alle_seen})

        # Szenarien-Spalten mit gewünschtem Namen hinzufügen
        for szenario in szenarien:
            colname = f"Aussterbejahr bei {szenario}"
            if szenario in df_sterbejahr.columns:
                result[colname] = result['lake'].map(df_sterbejahr[szenario])
            else:
                result[colname] = 0  # oder np.nan

        results.append(result)

    # Alle Ergebnisse zusammenfügen
    return pd.concat(results, ignore_index=True)



def seen_mit_sterbejahr_single(df_merged: pd.DataFrame, fisch_name, szenarien=None) -> pd.DataFrame:
    """
    Gibt für einen Fisch alle Seen aus, in denen er vorkommt, und für jedes Szenario das Jahr,
    in dem der Fisch stirbt. Die Spaltennamen verwenden das Label statt des Szenario-Codes.
    Die Seen werden so sortiert, dass die mit den meisten 0en (d.h. nie Aussterben) unten stehen.
    """
    labels = {"RCP26": "Optimistisches Szenario", "RCP45": "Mittleres Szenario", "RCP85": "Pessimistisches Szenario"}

    if szenarien is None:
        szenarien = ['RCP26', 'RCP45', 'RCP85']

    # Filter für den angegebenen Fisch
    df_fisch = df_merged[df_merged['Fisch'] == fisch_name]

    # Gruppieren nach lake und scenario, frühestes Sterbejahr mit get_death_year ermitteln
    df_sterbejahr = (
        df_fisch.groupby(['lake', 'scenario'])
        .apply(get_death_year, include_groups=False)
        .unstack(fill_value=0)
    )

    # Alle Seen, in denen der Fisch vorkommt
    alle_seen = df_fisch['lake'].unique()

    # DataFrame erstellen mit allen Seen
    result = pd.DataFrame({'lake': alle_seen})

    # Szenarien-Spalten mit Label als Namen hinzufügen
    label_colnames = []
    for szenario in szenarien:
        label = labels.get(szenario, szenario)
        colname = label
        label_colnames.append(colname)
        if szenario in df_sterbejahr.columns:
            result[colname] = result['lake'].map(df_sterbejahr[szenario])
        else:
            result[colname] = 0  # oder np.nan

    # Sortieren: Je mehr 0en pro See (über alle Label-Spalten), desto weiter unten
    result['anzahl_0'] = (result[label_colnames] == 0).sum(axis=1)
    result = result.sort_values('anzahl_0').reset_index(drop=True)
    result = result.drop(columns='anzahl_0')

    return result


###########################################################################################

def to_rgba(color: str, alpha: float = 0.3) -> str:
    """
    Convert a color string to an RGBA string with the specified alpha value.

    Args:
        color (str): Color as 'rgb(R,G,B)', '#RRGGBB', or 'rgba(R,G,B,A)'.
        alpha (float, optional): Alpha value for transparency (0 to 1). Defaults to 0.3.

    Returns:
        str: Color as 'rgba(R,G,B,alpha)' or original string if conversion fails.
    """
    if isinstance(color, str) and color.startswith("rgb("):
        nums = re.findall(r'\d+', color)
        return f"rgba({nums[0]},{nums[1]},{nums[2]},{alpha})"
    elif isinstance(color, str) and color.startswith("#"):
        h = color.lstrip("#")
        return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{alpha})"
    elif isinstance(color, str) and color.startswith("rgba("):
        # Replace alpha value
        return re.sub(r'rgba\((\d+),(\d+),(\d+),[0-9.]+\)', 
                      fr'rgba(\1,\2,\3,{alpha})', color)
    else:
        return color
    


# interactive graph for Dashboard
def plot_scenario(
    df_forelle: pd.DataFrame,
    see: str,
    fisch: str,
    window: int = 10
    ) -> go.Figure:

    """
    Plots the scenario temperature development for a given lake and fish as an interactive Plotly figure.
    All text except the subtitle is black.
    The legend is always visible.
    """
    
    # Farben und Labels für Szenarien
    farben = {"RCP26": "#2ca02c", "RCP45": "#ff9900", "RCP85": "#e41a1c"}
    labels = {"RCP26": "Optimistisches Szenario", "RCP45": "Mittleres Szenario", "RCP85": "Pessimistisches Szenario"}

    df_plot = df_forelle[df_forelle["lake"] == see]
    df_plot_grouped = df_plot.groupby(["year", "scenario"]).agg({
        "temperature_avg": "mean",
        "Kritische Temperatur °C": "first"
    }).reset_index()

    fig = go.Figure()
    krit_temp = df_plot_grouped["Kritische Temperatur °C"].iloc[0]

    for i, scenario in enumerate(df_plot_grouped["scenario"].unique()):
        gruppe = df_plot_grouped[df_plot_grouped["scenario"] == scenario].sort_values("year")
        years = gruppe["year"].to_numpy()
        farbe = farben.get(scenario, "gray")

        rolling_avg = gruppe["temperature_avg"].rolling(window=window, min_periods=1).mean().to_numpy()
        rolling_std = gruppe["temperature_avg"].rolling(window=window, min_periods=1).std().to_numpy()
        upper = rolling_avg + rolling_std
        lower = rolling_avg - rolling_std

        # Gray area for noise (1 std) - always
        fig.add_traces([
            go.Scatter(
                x=years,
                y=upper,
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ),
            go.Scatter(
                x=years,
                y=lower,
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.15)',
                line=dict(width=0),
                name='Noise (1 Std)' if i == 0 else None,
                legendgroup='noise',
                hoverinfo='skip',
                showlegend=True if i == 0 else False
            )
        ])

        # Area for noise (1 std) - only above critical value, in line color with alpha 0.3
        mask = upper > krit_temp
        upper_noise = np.where(mask, upper, np.nan)
        lower_noise = np.where(mask, np.maximum(lower, krit_temp), np.nan)
        fig.add_trace(go.Scatter(
            x=years,
            y=upper_noise,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=years,
            y=lower_noise,
            mode='lines',
            fill='tonexty',
            fillcolor=to_rgba(farbe, 0.3),  # line color with alpha 0.3
            line=dict(width=0),
            name=None,
            showlegend=False,
            hoverinfo='skip'
        ))

        # Main rolling average line
        fig.add_trace(go.Scatter(
            x=years,
            y=rolling_avg,
            mode='lines',
            name=labels.get(scenario, scenario),
            line=dict(color=farbe, width=2.5),
            legendgroup=scenario,
            showlegend=True  # <--- Legende immer sichtbar!
        ))

        # Exceedance year
        exceed = np.where(rolling_avg > krit_temp)[0]
        if len(exceed) > 0:
            exceed_index = exceed[0]
            year_dead = years[exceed_index]
            temp_dead = rolling_avg[exceed_index]
            fig.add_trace(go.Scatter(
                x=[year_dead],
                y=[temp_dead],
                mode='markers+text',
                marker=dict(color=farbe, size=10),
                text=[f"ab {year_dead}"],
                textposition="top right",
                showlegend=False,
                hoverinfo='text',
                textfont=dict(
                    color="black",
                    size=12,
                    family="Arial Black"
                )
            ))

    # Critical temperature line
    fig.add_trace(go.Scatter(
        x=years,
        y=[krit_temp]*len(years),
        mode='lines',
        line=dict(color='red', dash='dot', width=1.5),
        name=f"Krit. Temp. ({krit_temp:.1f} °C)",
        legendgroup='krit',
        showlegend=True  # <--- Legende immer sichtbar!
    ))

    fig.update_layout(
        font=dict(color='black'),  # Alle Schrift schwarz
        title=dict(
            text=f"{fisch} in {see}",
            font=dict(size=18, color="black"),
            x=0.5,
            xanchor='center',
            subtitle=dict(
                text="Temperaturverlauf der Klimaszenarien, geglättet über 10 Jahre",
                font=dict(size=14, color="gray")
            )
        ),
        xaxis_title="Jahr",
        yaxis_title="Ø Temperatur [°C]",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1,
            font=dict(color='black')
        ),
        hovermode="x unified",
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',   # Plotfläche transparent
        paper_bgcolor='rgba(0,0,0,0)',  # Gesamter Hintergrund transparent
    )

    # Remove gridlines
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig




# animated graph for data story

# animated the lines only 
def plot_forelle_scenario_animated_lines(
    df_forelle: pd.DataFrame,
    see: str,
    fisch: str,
    farben: dict,
    labels: dict,
    window: int = 10
) -> 'go.Figure':
    """
    Animated line plot for scenarios, animating lines from bottom to top.
    All text except the subtitle is black. Subtitle is gray.
    Animation starts automatically when exported to HTML with auto_play=True.
    """
    import numpy as np
    import plotly.graph_objects as go

    # Prepare data
    df_plot = df_forelle[df_forelle["lake"] == see]
    df_plot_grouped = df_plot.groupby(["year", "scenario"]).agg({
        "temperature_avg": "mean",
        "Kritische Temperatur °C": "first"
    }).reset_index()
    years_all = sorted(df_plot_grouped["year"].unique())

    # Calculate global x and y ranges for all traces
    x_min = df_plot_grouped["year"].min()
    x_max = df_plot_grouped["year"].max()

    y_values = []
    for scenario in df_plot_grouped["scenario"].unique():
        gruppe = df_plot_grouped[df_plot_grouped["scenario"] == scenario].sort_values("year")
        rolling_avg = gruppe["temperature_avg"].rolling(window=window, min_periods=1).mean()
        y_values.extend(rolling_avg)
    y_values.extend(df_plot_grouped["Kritische Temperatur °C"].unique())
    y_min = float(np.nanmin(y_values))
    y_max = float(np.nanmax(y_values))

    fig = go.Figure()

    fig.update_layout(
        font=dict(color='black'),  # Set all text to black by default
        title=dict(
            text=f"{fisch} in {see}",
            font=dict(size=18, color="black"),
            x=0.5,
            xanchor='center',
            subtitle=dict(
                text="Temperaturverlauf der Klimaszenarien, geglättet über 10 Jahre",
                font=dict(size=14, color="gray")  # Subtitle in gray
            )
        ),
        xaxis_title="Jahr",
        yaxis_title="Ø Temperatur [°C]",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1,
            font=dict(color='black')  # Legend text in black (redundant, but explicit)
        ),
        hovermode="x unified",
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "buttons": [{
                "label": "Play",
                "method": "animate",
                "args": [
                    None,
                    {
                        "frame": {"duration": 60, "redraw": True},
                        "fromcurrent": True,
                        "autoplay": True  # This is ignored except in HTML export with auto_play
                    }
                ]
            }]
        }]
    )
    
    # Set x and y axis ranges and black color for axis lines/ticks
    fig.update_xaxes(
        range=[x_min, x_max],
        color='black',
        showgrid=False
    )
    fig.update_yaxes(
        range=[y_min, y_max],
        color='black',
        showgrid=False
    )

    # Build frames
    frames = []
    for frame_year in years_all:
        frame_data = []
        for i, scenario in enumerate(df_plot_grouped["scenario"].unique()):
            gruppe = df_plot_grouped[df_plot_grouped["scenario"] == scenario].sort_values("year")
            years = gruppe["year"].to_numpy()
            mask_frame = years <= frame_year
            years_visible = years[mask_frame]
            if len(years_visible) == 0:
                continue
            farbe = farben.get(scenario, "gray")
            rolling_avg = gruppe["temperature_avg"].rolling(window=window, min_periods=1).mean().to_numpy()[mask_frame]
            # Animated main line
            frame_data.append(go.Scatter(
                x=years_visible,
                y=rolling_avg,
                mode='lines',
                name=labels.get(scenario, scenario),
                line=dict(color=farbe, width=2.5),
                legendgroup=scenario,
                showlegend=True

            ))
        # Critical temperature line (fixed)
        krit_temp = gruppe["Kritische Temperatur °C"].iloc[0]
        frame_data.append(go.Scatter(
            x=years_all,
            y=[krit_temp]*len(years_all),
            mode='lines',
            line=dict(color='red', dash='dot', width=1.5),
            name=f"Krit. Temp. ({krit_temp:.1f} °C)",
            legendgroup='krit',
            showlegend=True

        ))
        frames.append(go.Frame(data=frame_data, name=str(frame_year)))

    fig.add_traces(frames[0].data)
    fig.frames = frames

    return fig
