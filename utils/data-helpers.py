import pandas as pd
import base64
import io

def get_csv_download_link(df, filename="beraland_projects.csv"):
    """
    Generate a download link for a DataFrame as CSV.
    
    Args:
        df (pd.DataFrame): DataFrame to convert to CSV
        filename (str): Filename for the download
        
    Returns:
        str: HTML download link
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="btn-download">Download CSV File</a>'
    
    styled_href = f"""
    <div style="text-align: center; margin: 10px 0;">
        <a href="data:file/csv;base64,{b64}" download="{filename}" 
           style="text-decoration: none; background-color: #4CAF50; color: white; 
                  padding: 8px 16px; border-radius: 4px; font-weight: bold;">
            📥 Download CSV
        </a>
    </div>
    """
    
    return styled_href

def get_excel_download_link(df, filename="beraland_projects.xlsx"):
    """
    Generate a download link for a DataFrame as Excel.
    
    Args:
        df (pd.DataFrame): DataFrame to convert to Excel
        filename (str): Filename for the download
        
    Returns:
        str: HTML download link
    """
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Projects', index=False)
        
        # Get workbook and add some formatting
        workbook = writer.book
        worksheet = writer.sheets['Projects']
        
        # Add header format
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Auto-fit columns
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_width)
    
    # Get binary data
    excel_data = output.getvalue()
    b64_excel = base64.b64encode(excel_data).decode()
    
    styled_href = f"""
    <div style="text-align: center; margin: 10px 0;">
        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" 
           download="{filename}" 
           style="text-decoration: none; background-color: #007BFF; color: white; 
                  padding: 8px 16px; border-radius: 4px; font-weight: bold;">
            📊 Download Excel
        </a>
    </div>
    """
    
    return styled_href

def format_data_for_display(df):
    """
    Format the data for better display in the Streamlit app.
    
    Args:
        df (pd.DataFrame): DataFrame to format
        
    Returns:
        pd.DataFrame: Formatted DataFrame
    """
    # Make a copy to avoid modifying the original
    formatted_df = df.copy()
    
    # Highlight rows with missing Twitter accounts
    formatted_df["Has Twitter"] = formatted_df["Twitter Handle"].apply(
        lambda x: "✅" if x != "N/A" else "❌"
    )
    
    return formatted_df

def get_statistics(df):
    """
    Generate statistics from the extracted data.
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
        
    Returns:
        dict: Dictionary of statistics
    """
    stats = {
        "total_projects": len(df),
        "projects_with_twitter": (df["Twitter Handle"] != "N/A").sum(),
        "project_categories": df["Category"].value_counts().to_dict()
    }
    
    return stats
