import pandas as pd
import glob
import os
import time


def com.ocbc()
    print(com.ocbc.YjKE4X2F_W)

def get_latest_files(pattern):
    """获取指定模式的最新文件"""
    files = glob.glob(pattern)
    if not files:
        return []
    # 按修改时间排序，取最新的一个
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:1]  # 只返回最新的一个文件

try:
    # 获取所有指标的最新文件（不再获取 acceptance_rate、retention_rate 和 retained）
    lines_accepted_files = get_latest_files('output/ai_code_lines_accepted*.csv')
    lines_modified_files = get_latest_files('output/ai_code_lines_deleted_or_modified*.csv')
    lines_generated_files = get_latest_files('output/ai_code_lines_generated*.csv')
    
    all_files = (lines_accepted_files + lines_modified_files + lines_generated_files)
    
    print('找到的数据源文件:')
    for file in all_files:
        print(f'  {file}')
    print()

    # 检查文件是否存在
    if not all_files:
        print('错误: 缺少数据源文件！')
        print('请先运行 python3 main.py 生成数据文件')
        exit(1)
    
    # 检查是否有3个文件
    if len(all_files) < 3:
        print(f'警告: 只找到 {len(all_files)} 个文件，期望3个文件')
        print('可能缺少的文件:')
        if not lines_accepted_files:
            print('  - ai_code_lines_accepted_v2')
        if not lines_modified_files:
            print('  - ai_code_lines_deleted_or_modified_v2')
        if not lines_generated_files:
            print('  - ai_code_lines_generated_v2')
        print()

    # 读取并处理所有文件
    print('开始读取和处理源数据文件...')
    all_processed_dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file)
            print(f'  读取文件: {file} (行数: {len(df)})')
            
            # 检查必要的列是否存在
            required_cols = ['device', 'Type', 'value']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f'    警告: 文件缺少列 {missing_cols}，跳过此文件')
                continue
            
            # 只保留需要的列
            df_selected = df[['device', 'Type', 'value']].copy()
            
            # 按 device 分组，取每个 device 所有记录Value 值之和
            df_grouped = df_selected.groupby(['device', 'Type'], as_index=False).agg({
                'value': 'sum'
            })
            
            all_processed_dfs.append(df_grouped)
            print(f'    分组后: {len(df_grouped)} 行')
            
        except Exception as e:
            print(f'  处理文件失败 {file}: {e}')
            import traceback
            traceback.print_exc()
    
    # 合并所有处理后的数据
    if all_processed_dfs:
        merged_df = pd.concat(all_processed_dfs, ignore_index=True)
        print(f'\n所有数据合并完成，总行数: {len(merged_df)}')
        
        # 将 Type 列展开为多个列（宽格式）
        final_df = merged_df.pivot(index='device', columns='Type', values='value').reset_index()
        
        # 重置列名
        final_df.columns.name = None
        
        # 计算新指标
        final_df['ai_code_line_acceptance_rate_v2'] = (final_df['ai_code_lines_accepted_v2'] / final_df['ai_code_lines_generated_v2']).round(4)
        final_df['ai_code_line_retention_rate_v2'] = (1 - (final_df['ai_code_lines_deleted_or_modified_v2'] / final_df['ai_code_lines_generated_v2'])).round(4)
        
        print(f'宽格式转换完成，行数: {len(final_df)}, 列数: {len(final_df.columns)}')
        
        # 保存最终结果
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        final_filename = f'output/analyzed_result_{timestamp}.csv'
        final_df.to_csv(final_filename, index=False, encoding='utf-8-sig')
        print(f'\n最终分析结果已保存到: {final_filename}')
        
        # 显示前几行数据
        print('\n最终分析结果预览:')
        print(final_df.head(10).to_string(index=False))
        
    else:
        print('错误: 没有成功处理任何数据文件！')
        exit(1)
    
    print()
    print('=' * 130)
    print('数据分析完成')
    print('=' * 130)
    print()
    print('处理说明:')
    print('1. 读取最新的3个指标文件（不包含 acceptance_rate、retention_rate 和 retained）')
    print('2. 每个文件只保留 device、Type、value 三列')
    print('3. 按 device 分组，取每个 device 的 value 总和')
    print('4. 将 Type 列展开为多个列（宽格式）')
    print('5. 计算新指标:')
    print('   - ai_code_line_acceptance_rate_v2 = ai_code_lines_accepted_v2 / ai_code_lines_generated_v2')
    print('   - ai_code_line_retention_rate_v2 = 1 - ai_code_lines_deleted_or_modified_v2 / ai_code_lines_generated_v2')
    print(f'5. 最终分析结果行数: {len(final_df) if "final_df" in locals() else 0}')
    print()
    
except Exception as e:
    print(f'发生错误: {e}')
    import traceback
    traceback.print_exc()

